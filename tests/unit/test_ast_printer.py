import unittest

from protolang.ast_printer import format_ast_as_mermaid
from protolang.diagnostics import DiagnosticReporter
from protolang.lexer import Lexer
from protolang.parser import Parser


class ASTPrinterTests(unittest.TestCase):
    def parse(self, source: str):
        reporter = DiagnosticReporter(source, filename="test_code")
        lexer = Lexer(source, reporter=reporter)
        parser = Parser(lexer, reporter=reporter)
        ast = parser.parse_program()
        self.assertFalse(reporter.has_errors(), msg=reporter.format())
        return ast

    def test_format_ast_as_mermaid_uses_field_names_as_edge_labels(self):
        """Use AST field names as Mermaid edge labels"""
        ast = self.parse("function main() { while (1) { 2; } }")

        actual = format_ast_as_mermaid(ast)

        self.assertTrue(actual.startswith("graph TD"))
        self.assertIn('["WhileStatement"]', actual)
        self.assertIn("-->|condition|", actual)
        self.assertIn("-->|body|", actual)

    def test_format_ast_as_mermaid_uses_indexed_labels_for_ast_lists(self):
        """Use indexed Mermaid edge labels for AST lists"""
        ast = self.parse("function main(a, b) { var x = 1; x; return b; }")

        actual = format_ast_as_mermaid(ast)

        self.assertIn("-->|items.0|", actual)
        self.assertIn("-->|items.1|", actual)
        self.assertIn("-->|items.2|", actual)

    def test_format_ast_as_mermaid_embeds_non_ast_fields_in_node_label(self):
        """Embed non-AST field values in Mermaid node labels"""
        ast = self.parse("function main(a, b) { 1 + 2; }")

        actual = format_ast_as_mermaid(ast)

        self.assertIn("name=main", actual)
        self.assertIn("params=[a, b]", actual)
        self.assertIn("op=PLUS", actual)
        self.assertIn("value=1", actual)
        self.assertIn("value=2", actual)


if __name__ == "__main__":
    unittest.main()
