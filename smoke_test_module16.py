"""Module 16 smoke test — full reproduction of reference/module16_practice_worksheet.pdf.

5 pages: Type 1 (Adding) + Type 2 (Subtracting) + Type 3 (Perimeter Word) +
Type 4 (Real-World Applications) + Answer Key. Compare smoke_module16.pdf to
the reference page-by-page; positions should be within ~5pt across the board.

Run with:  python smoke_test_module16.py
Output:    smoke_module16.pdf
"""

from worksheet_renderer import Problem, ProblemType, Worksheet, render_worksheet


TYPE_1 = ProblemType(
    number=1,
    title="Adding Polynomials (Find the Sum)",
    answer_key_title="Adding Polynomials",
    instruction="Find each sum. Show all work. Circle your final answer.",
    layout="centered",
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


TYPE_2 = ProblemType(
    number=2,
    title="Subtracting Polynomials (Find the Difference)",
    answer_key_title="Subtracting Polynomials",
    instruction="Find each difference. Show all work. Circle your final answer.",
    layout="centered",
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


TYPE_3 = ProblemType(
    number=3,
    title="Polynomial Perimeter Word Problems",
    answer_key_title="Perimeter Word Problems",
    instruction="Find each perimeter. Show all work. Circle your final answer.",
    layout="word_setup",
    example_lines=[
        "Find the perimeter of a triangle with sides (2m+5), (10m^2-8), and (m^2+8m).",
        "P = (2m+5) + (10m^2-8) + (m^2+8m)",
        "Combine like terms: (10m^2+m^2) + (2m+8m) + (5-8)",
        "Answer: 11m^2 + 10m - 3.  Use P = Side + Side + Side.",
    ],
    problems=[
        Problem(label="3-A",
                body="Find the perimeter of a triangle with sides (3x + 2) in., (5x - 1) in., and (2x + 4) in.",
                setup="P = (3x + 2) + (5x - 1) + (2x + 4)",
                answer="P = 10x + 5"),
        Problem(label="3-B",
                body="Find the perimeter of a triangle with sides (m^2 + 2m) ft, (3m^2 - 5) ft, and (2m + 7) ft.",
                setup="P = (m^2 + 2m) + (3m^2 - 5) + (2m + 7)",
                answer="P = 4m^2 + 4m + 2"),
        Problem(label="3-C",
                body="Find the perimeter of a triangle with sides (2n^2 - 3) cm, (n^2 + 4n) cm, and (3n + 6) cm.",
                setup="P = (2n^2 - 3) + (n^2 + 4n) + (3n + 6)",
                answer="P = 3n^2 + 7n + 3"),
        Problem(label="3-D",
                body="Find the perimeter of a triangle with sides (4a + 3) m, (2a^2 - a) m, and (a^2 + 5a + 1) m.",
                setup="P = (4a + 3) + (2a^2 - a) + (a^2 + 5a + 1)",
                answer="P = 3a^2 + 8a + 4"),
        Problem(label="3-E",
                body="Find the perimeter of a triangle with sides (5k^2 - 2k) yd, (3k + 7) yd, and (2k^2 + k - 3) yd.",
                setup="P = (5k^2 - 2k) + (3k + 7) + (2k^2 + k - 3)",
                answer="P = 7k^2 + 2k + 4"),
    ],
)


TYPE_4 = ProblemType(
    number=4,
    title="Real-World Polynomial Applications",
    answer_key_title="Real-World Applications",
    instruction="Write a simplified profit expression, then evaluate. Show all work.",
    layout="word_blanks",
    example_lines=[
        "Revenue: (15x^3 + 6x^2 + 700) dollars. Cost: (60x^2 + 2000) dollars.",
        "Profit = Revenue - Cost",
        "= (15x^3 + 6x^2 + 700) - (60x^2 + 2000)",
        "= 15x^3 - 54x^2 - 1300.  Then substitute the given x to find profit.",
    ],
    problems=[
        Problem(label="4-A",
                body="The revenue for a company selling x products is modeled by (8x^3 + 4x^2 + 300) dollars. The operating cost is modeled by (3x^2 + 800) dollars. Write a simplified expression for the profit. Then find the profit if x = 5.",
                blanks=["Profit expression:", "If x = 5, profit ="],
                answer="Profit = 8x^3 + x^2 - 500; at x=5: $525"),
        Problem(label="4-B",
                body="The revenue for a company selling x products is modeled by (12x^3 + 8x^2 + 400) dollars. The operating cost is modeled by (50x^2 + 1200) dollars. Write a simplified expression for the profit. Then find the profit if x = 8.",
                blanks=["Profit expression:", "If x = 8, profit ="],
                answer="Profit = 12x^3 - 42x^2 - 800; at x=8: $2,656"),
        Problem(label="4-C",
                body="The revenue for a company selling x products is modeled by (20x^2 + 5x + 900) dollars. The operating cost is modeled by (8x^2 + 600) dollars. Write a simplified expression for the profit. Then find the profit if x = 4.",
                blanks=["Profit expression:", "If x = 4, profit ="],
                answer="Profit = 12x^2 + 5x + 300; at x=4: $512"),
        Problem(label="4-D",
                body="The revenue for a company selling x products is modeled by (6x^3 + 10x^2 + 200) dollars. The operating cost is modeled by (2x^2 + 750) dollars. Write a simplified expression for the profit. Then find the profit if x = 6.",
                blanks=["Profit expression:", "If x = 6, profit ="],
                answer="Profit = 6x^3 + 8x^2 - 550; at x=6: $1,034"),
        Problem(label="4-E",
                body="The revenue for a company selling x products is modeled by (15x^3 + 6x^2 + 700) dollars. The operating cost is modeled by (60x^2 + 2000) dollars. Write a simplified expression for the profit. Then find the profit if x = 10.",
                blanks=["Profit expression:", "If x = 10, profit ="],
                answer="Profit = 15x^3 - 54x^2 - 1300; at x=10: $8,300"),
    ],
)


def main() -> None:
    worksheet = Worksheet(
        title="Adding & Subtracting Polynomials — Practice Worksheet",
        types=[TYPE_1, TYPE_2, TYPE_3, TYPE_4],
    )
    render_worksheet(worksheet, "smoke_module16.pdf")
    print("Wrote smoke_module16.pdf")


if __name__ == "__main__":
    main()
