from __future__ import annotations

from dataclasses import fields
from enum import Enum

from .ast import ASTNode


_SKIP_FIELDS = {
    "span",
    "name_span",
    "func_name_span",
    "param_spans",
    "var_info",
    "function_info",
}


def format_ast_as_mermaid(node: object) -> str:
    builder = _MermaidASTBuilder()
    builder.add_root(node)
    return builder.format()


class _MermaidASTBuilder:
    def __init__(self) -> None:
        self.next_id = 0
        self.nodes: list[str] = []
        self.edges: list[str] = []

    def add_root(self, value: object) -> None:
        if isinstance(value, ASTNode):
            self._add_ast_node(value)
        elif isinstance(value, list):
            root_id = self._new_id()
            self.nodes.append(f'{root_id}["list"]')
            for index, item in enumerate(value):
                if isinstance(item, ASTNode):
                    child_id = self._add_ast_node(item)
                    self.edges.append(f"{root_id} -->|[{index}]| {child_id}")
                else:
                    child_id = self._add_scalar_node(item)
                    self.edges.append(f"{root_id} -->|[{index}]| {child_id}")
        else:
            self._add_scalar_node(value)

    def format(self) -> str:
        lines = ["graph TD"]
        if self.nodes:
            lines.append("")
            lines.extend(self.nodes)
        if self.edges:
            lines.append("")
            lines.extend(self.edges)
        return "\n".join(lines)

    def _add_ast_node(self, node: ASTNode) -> str:
        node_id = self._new_id()
        label_lines = [node.__class__.__name__]

        child_links: list[tuple[str, ASTNode]] = []
        scalar_links: list[tuple[str, object]] = []

        for field in fields(node):
            if field.name in _SKIP_FIELDS:
                continue
            field_value = getattr(node, field.name)
            if field_value is None:
                continue
            if isinstance(field_value, ASTNode):
                child_links.append((field.name, field_value))
            elif isinstance(field_value, list):
                if all(isinstance(item, ASTNode) for item in field_value):
                    for index, item in enumerate(field_value):
                        child_links.append((f"{field.name}.{index}", item))
                else:
                    formatted_items = ", ".join(
                        _format_scalar(item) for item in field_value
                    )
                    label_lines.append(f"{field.name}=[{formatted_items}]")
            else:
                label_lines.append(f"{field.name}={_format_scalar(field_value)}")

        self.nodes.append(
            f'{node_id}["{_escape_mermaid_label(chr(10).join(label_lines))}"]'
        )

        for edge_label, child_node in child_links:
            child_id = self._add_ast_node(child_node)
            self.edges.append(
                f"{node_id} -->|{_escape_mermaid_edge_label(edge_label)}| {child_id}"
            )

        for edge_label, scalar_value in scalar_links:
            child_id = self._add_scalar_node(scalar_value)
            self.edges.append(
                f"{node_id} -->|{_escape_mermaid_edge_label(edge_label)}| {child_id}"
            )

        return node_id

    def _add_scalar_node(self, value: object) -> str:
        node_id = self._new_id()
        label = _format_scalar(value)
        self.nodes.append(f'{node_id}["{_escape_mermaid_label(label)}"]')
        return node_id

    def _new_id(self) -> str:
        node_id = f"n{self.next_id}"
        self.next_id += 1
        return node_id


def _format_scalar(value: object) -> str:
    if isinstance(value, Enum):
        return value.name
    return str(value)


def _escape_mermaid_label(label: str) -> str:
    return label.replace("\\", "\\\\").replace('"', "&quot;").replace("\n", "<br/>")


def _escape_mermaid_edge_label(label: str) -> str:
    return label.replace("|", "&#124;")
