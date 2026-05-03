"""Step 2 smoke test for worksheet_renderer.

Renders the full Type 1 page from module 16 — Adding Polynomials, all
five problems with exponent markup where the reference has them. Output
should be a near-pixel match to reference/module16_practice_worksheet.pdf
page 1: title + rule, Name/Date/Period blanks, NAVY section header,
cream/tan example box, instruction line, five evenly-distributed
problems with light-gray separators, and exponents rendered as true
raised superscripts (no black boxes, no Unicode).

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
            Problem(
                label="1-B",
                prompt="Find the sum.",
                body="(7ab - 3ac + bc) + (2ab + 6ac - 5bc)",
                answer="9ab + 3ac - 4bc",
            ),
            Problem(
                label="1-C",
                prompt="Find the sum.",
                body="(4m^2n - 3mn^2 + 2mn) + (-m^2n + 5mn^2 - 7mn)",
                answer="3m^2n + 2mn^2 - 5mn",
            ),
            Problem(
                label="1-D",
                prompt="Find the sum.",
                body="(8x^2y + 3xy^2 - xy) + (-2x^2y - xy^2 + 4xy)",
                answer="6x^2y + 2xy^2 + 3xy",
            ),
            Problem(
                label="1-E",
                prompt="Find the sum.",
                body="(-5a^2b + 4ab^2 - 3ab) + (3a^2b - 2ab^2 + 8ab)",
                answer="-2a^2b + 2ab^2 + 5ab",
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
