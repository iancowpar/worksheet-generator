"""Step 3 smoke test for worksheet_renderer.

Renders Types 1 and 2 from module 16 (both centered-expression layout)
plus the answer key page. Output should be 3 pages:

  Page 1 — Type 1 (Adding Polynomials, 5 problems with exponents)
  Page 2 — Type 2 (Subtracting Polynomials, 5 problems with exponents)
  Page 3 — Answer Key (both types, label + answer rows)

Compare to reference/module16_practice_worksheet.pdf pages 1, 2, and 5.
Word-problem variant layouts (module 16 Types 3 and 4) and MC/table/
short-answer layouts (module 13/14) come in Step 4.

Run with:  python smoke_test.py
Output:    smoke_output.pdf
"""

from worksheet_renderer import (
    Problem,
    ProblemType,
    Worksheet,
    render_worksheet,
)


def main() -> None:
    type_1 = ProblemType(
        number=1,
        title="Adding Polynomials (Find the Sum)",
        answer_key_title="Adding Polynomials",
        instruction="Find each sum. Show all work. Circle your final answer.",
        example_lines=[
            "Find the sum: (5ab + 5ac - 9bc) + (-ab + 10ac + 4bc)",
            "Group like terms: (5ab - ab) + (5ac + 10ac) + (-9bc + 4bc)",
            "Simplify: 4ab + 15ac + -5bc",
            "Answer: 4ab + 15ac - 5bc.  Show all work!",
        ],
        problems=[
            Problem(label="1-A", prompt="Find the sum.",
                    body="(3xy + 2xz - 4yz) + (-xy + 5xz + 2yz)",
                    answer="2xy + 7xz - 2yz"),
            Problem(label="1-B", prompt="Find the sum.",
                    body="(7ab - 3ac + bc) + (2ab + 6ac - 5bc)",
                    answer="9ab + 3ac - 4bc"),
            Problem(label="1-C", prompt="Find the sum.",
                    body="(4m^2n - 3mn^2 + 2mn) + (-m^2n + 5mn^2 - 7mn)",
                    answer="3m^2n + 2mn^2 - 5mn"),
            Problem(label="1-D", prompt="Find the sum.",
                    body="(8x^2y + 3xy^2 - xy) + (-2x^2y - xy^2 + 4xy)",
                    answer="6x^2y + 2xy^2 + 3xy"),
            Problem(label="1-E", prompt="Find the sum.",
                    body="(-5a^2b + 4ab^2 - 3ab) + (3a^2b - 2ab^2 + 8ab)",
                    answer="-2a^2b + 2ab^2 + 5ab"),
        ],
    )

    type_2 = ProblemType(
        number=2,
        title="Subtracting Polynomials (Find the Difference)",
        answer_key_title="Subtracting Polynomials",
        instruction="Find each difference. Show all work. Circle your final answer.",
        example_lines=[
            "Find the difference: (-12r^2s + 2rs^2 + 6rs) - (3r^2s + 8rs^2 - rs)",
            "Distribute the negative: -12r^2s + 2rs^2 + 6rs - 3r^2s - 8rs^2 + rs",
            "Combine like terms: -15r^2s - 6rs^2 + 7rs",
            "Answer: -15r^2s - 6rs^2 + 7rs.  Show all work!",
        ],
        problems=[
            Problem(label="2-A", prompt="Find the difference.",
                    body="(6x^2y - 3xy^2 + 5xy) - (2x^2y + xy^2 - 3xy)",
                    answer="4x^2y - 4xy^2 + 8xy"),
            Problem(label="2-B", prompt="Find the difference.",
                    body="(8ab^2 - 5a^2b + 3ab) - (-2ab^2 + 4a^2b + ab)",
                    answer="10ab^2 - 9a^2b + 2ab"),
            Problem(label="2-C", prompt="Find the difference.",
                    body="(5m^2n - 3mn + 2mn^2) - (2m^2n + mn - 4mn^2)",
                    answer="3m^2n - 4mn + 6mn^2"),
            Problem(label="2-D", prompt="Find the difference.",
                    body="(-4r^2s + 7rs^2 - 2rs) - (3r^2s - 2rs^2 + 5rs)",
                    answer="-7r^2s + 9rs^2 - 7rs"),
            Problem(label="2-E", prompt="Find the difference.",
                    body="(9x^2z - 4xz^2 + 6xz) - (-x^2z + 2xz^2 - 3xz)",
                    answer="10x^2z - 6xz^2 + 9xz"),
        ],
    )

    worksheet = Worksheet(
        title="Adding & Subtracting Polynomials — Practice Worksheet",
        types=[type_1, type_2],
    )

    output_path = "smoke_output.pdf"
    render_worksheet(worksheet, output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
