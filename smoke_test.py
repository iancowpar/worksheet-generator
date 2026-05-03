"""Step 1 smoke test for worksheet_renderer.

Renders a single page that should read as 'from the same family' as
reference/module16_practice_worksheet.pdf page 1: header + section
header + example box + one problem. Distribution math, exponent
parsing, and additional layouts arrive in later steps.

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
        instruction="Find each sum. Show all work. Circle your final answer.",
        example_lines=[
            "Find the sum: (5ab + 5ac - 9bc) + (-ab + 10ac + 4bc)",
            "Group like terms: (5ab - ab) + (5ac + 10ac) + (-9bc + 4bc)",
            "Simplify: 4ab + 15ac + -5bc",
            "Answer: 4ab + 15ac - 5bc.  Show all work!",
        ],
        problems=[
            Problem(
                label="1-A",
                prompt="Find the sum.",
                body="(3xy + 2xz - 4yz) + (-xy + 5xz + 2yz)",
                answer="2xy + 7xz - 2yz",
            ),
        ],
    )

    worksheet = Worksheet(
        title="Adding & Subtracting Polynomials — Practice Worksheet",
        types=[type_1],
    )

    output_path = "smoke_output.pdf"
    render_worksheet(worksheet, output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
