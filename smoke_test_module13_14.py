"""Module 13/14 smoke test — full reproduction of reference/module13_14_practice_worksheet.pdf.

11 pages: Types 1-9 (one per page) + 2-page answer key. Exercises five layouts:
mc_2col, mc_4row, table, short_answer_right, short_answer_below. Compare
smoke_module13_14.pdf to the reference page-by-page.

Run with:  python smoke_test_module13_14.py
Output:    smoke_module13_14.pdf
"""

from worksheet_renderer import Problem, ProblemType, Worksheet, render_worksheet


TYPE_1 = ProblemType(
    number=1,
    title="Exponential Function from Two Points (MC)",
    answer_key_title="Exponential Function from Two Points",
    instruction="Find the exponential function. Circle the correct answer.",
    layout="mc_2col",
    example_lines=[
        "Which exponential function passes through (0, 21) and (1, 3)?",
        "y = a(b)^x.  At x=0: y=a, so a = 21.",
        "At x=1: y=ab=3, so b = 3/21 = 1/7.",
        "Function: y = 21(1/7)^x",
    ],
    problems=[
        Problem(label="1-A",
                body="Which exponential function passes through the points (0, 18) and (1, 6)?",
                options=["y = 6(1/3)^x", "y = 18(1/3)^x", "y = 18(3)^x", "y = 6(3)^x"],
                correct_letter="B",
                answer="(B) y = 18(1/3)^x"),
        Problem(label="1-B",
                body="Which exponential function passes through the points (0, 8) and (1, 24)?",
                options=["y = 24(1/3)^x", "y = 8(1/3)^x", "y = 8(3)^x", "y = 24(3)^x"],
                correct_letter="C",
                answer="(C) y = 8(3)^x"),
        Problem(label="1-C",
                body="Which exponential function passes through the points (0, 50) and (1, 10)?",
                options=["y = 50(1/5)^x", "y = 10(1/5)^x", "y = 10(5)^x", "y = 50(5)^x"],
                correct_letter="A",
                answer="(A) y = 50(1/5)^x"),
        Problem(label="1-D",
                body="Which exponential function passes through the points (0, 4) and (1, 12)?",
                options=["y = 12(1/3)^x", "y = 4(1/3)^x", "y = 4(3)^x", "y = 12(3)^x"],
                correct_letter="C",
                answer="(C) y = 4(3)^x"),
        Problem(label="1-E",
                body="Which exponential function passes through the points (0, 100) and (1, 25)?",
                options=["y = 100(1/4)^x", "y = 25(1/4)^x", "y = 25(4)^x", "y = 100(4)^x"],
                correct_letter="A",
                answer="(A) y = 100(1/4)^x"),
    ],
)


TYPE_2 = ProblemType(
    number=2,
    title="Find the nth Term in a Geometric Sequence (MC)",
    answer_key_title="nth Term in a Geometric Sequence",
    instruction="Find the requested term. Circle the correct answer.",
    layout="mc_2col",
    example_lines=[
        "What is the third term in f(n) = 2(0.8)^{n-1}?",
        "Substitute n=3: f(3) = 2(0.8)^2 = 2(0.64) = 1.28.  Answer: 1.28",
        "If given a sequence (no formula), find r = a_2 / a_1, then multiply.",
    ],
    problems=[
        Problem(label="2-A",
                body="What is the fourth term in the geometric sequence f(n) = 5(2)^{n-1}?",
                options=["20", "40", "80", "10"], correct_letter="B", answer="(B) 40"),
        Problem(label="2-B",
                body="What is the fifth term in the geometric sequence f(n) = 3(0.5)^{n-1}?",
                options=["0.375", "0.75", "0.1875", "1.5"], correct_letter="C", answer="(C) 0.1875"),
        Problem(label="2-C",
                body="What is the fifth term in the sequence 4, 12, 36, ...?",
                options=["108", "324", "972", "216"], correct_letter="B", answer="(B) 324"),
        Problem(label="2-D",
                body="What is the sixth term in the sequence 2, 10, 50, ...?",
                options=["1,250", "6,250", "31,250", "250"], correct_letter="B", answer="(B) 6,250"),
        Problem(label="2-E",
                body="What is the seventh term in the sequence 64, 32, 16, ...?",
                options=["1", "2", "4", "0.5"], correct_letter="A", answer="(A) 1"),
    ],
)


TYPE_3 = ProblemType(
    number=3,
    title="Recursive Rule from Explicit Formula (MC)",
    answer_key_title="Recursive Rule from Explicit Formula",
    instruction="Choose the correct recursive rule. Circle the correct answer.",
    layout="mc_2col",
    example_lines=[
        "Recursive rule for f(n) = 13(1.3)^{n-1}?",
        "First term: f(1) = 13.  Common ratio: 1.3.",
        "Recursive form: f(1) = 13, f(n) = 1.3 · f(n-1), n ≥ 2",
    ],
    problems=[
        Problem(label="3-A",
                body="What is the recursive rule for the geometric sequence f(n) = 13(1.3)^{n-1}?",
                options=[
                    "f(1) = 13, f(n-1) = 1.3 · f(n), n ≥ 2",
                    "f(1) = 1.3, f(n-1) = 13 · f(n), n ≥ 2",
                    "f(1) = 13, f(n) = 1.3 · f(n-1), n ≥ 2",
                    "f(1) = 1.3, f(n) = 13 · f(n-1), n ≥ 2",
                ],
                correct_letter="C",
                answer="(C) f(1) = 13, f(n) = 1.3 · f(n-1)"),
        Problem(label="3-B",
                body="What is the recursive rule for the geometric sequence f(n) = 5(2)^{n-1}?",
                options=[
                    "f(1) = 5, f(n) = 2 · f(n-1), n ≥ 2",
                    "f(1) = 2, f(n) = 5 · f(n-1), n ≥ 2",
                    "f(1) = 5, f(n-1) = 2 · f(n), n ≥ 2",
                    "f(1) = 2, f(n-1) = 5 · f(n), n ≥ 2",
                ],
                correct_letter="A",
                answer="(A) f(1) = 5, f(n) = 2 · f(n-1)"),
        Problem(label="3-C",
                body="What is the recursive rule for the geometric sequence f(n) = 8(0.5)^{n-1}?",
                options=[
                    "f(1) = 0.5, f(n) = 8 · f(n-1), n ≥ 2",
                    "f(1) = 8, f(n) = 0.5 · f(n-1), n ≥ 2",
                    "f(1) = 8, f(n-1) = 0.5 · f(n), n ≥ 2",
                    "f(1) = 0.5, f(n-1) = 8 · f(n), n ≥ 2",
                ],
                correct_letter="B",
                answer="(B) f(1) = 8, f(n) = 0.5 · f(n-1)"),
        Problem(label="3-D",
                body="What is the recursive rule for the geometric sequence f(n) = 100(0.1)^{n-1}?",
                options=[
                    "f(1) = 0.1, f(n) = 100 · f(n-1), n ≥ 2",
                    "f(1) = 100, f(n-1) = 0.1 · f(n), n ≥ 2",
                    "f(1) = 100, f(n) = 0.1 · f(n-1), n ≥ 2",
                    "f(1) = 0.1, f(n-1) = 100 · f(n), n ≥ 2",
                ],
                correct_letter="C",
                answer="(C) f(1) = 100, f(n) = 0.1 · f(n-1)"),
        Problem(label="3-E",
                body="What is the recursive rule for the geometric sequence f(n) = 7(4)^{n-1}?",
                options=[
                    "f(1) = 4, f(n) = 7 · f(n-1), n ≥ 2",
                    "f(1) = 7, f(n) = 4 · f(n-1), n ≥ 2",
                    "f(1) = 7, f(n-1) = 4 · f(n), n ≥ 2",
                    "f(1) = 4, f(n-1) = 7 · f(n), n ≥ 2",
                ],
                correct_letter="B",
                answer="(B) f(1) = 7, f(n) = 4 · f(n-1)"),
    ],
)


TYPE_4 = ProblemType(
    number=4,
    title="Linear vs. Exponential Growth (MC)",
    answer_key_title="Linear vs. Exponential Growth",
    instruction="Compare the two situations. Circle the correct answer.",
    layout="mc_4row",
    example_lines=[
        "Linear functions grow by a constant amount each step.",
        "Exponential growth functions multiply by a constant each step.",
        "Exponential growth ALWAYS overtakes linear growth eventually.",
    ],
    problems=[
        Problem(label="4-A",
                body="Andrew began with $20 in savings and increased his savings by $10 every month. Lindsay began with $5 in savings and doubled her savings every month. After Andrew and Lindsay each saved for 7 months, who saved more money?",
                options=[
                    "Andrew, because positive linear functions grow faster than exponential growth functions.",
                    "Andrew, because exponential growth functions eventually grow faster than positive linear functions.",
                    "Lindsay, because positive linear functions grow faster than exponential growth functions.",
                    "Lindsay, because exponential growth functions eventually grow faster than positive linear functions.",
                ],
                correct_letter="D",
                answer="(D) Lindsay (exponential eventually grows faster)"),
        Problem(label="4-B",
                body="Marcus began with $50 in savings and added $15 every week. Tia began with $3 in savings and tripled her savings every week. After 6 weeks, who saved more money?",
                options=[
                    "Marcus, because positive linear functions grow faster than exponential growth functions.",
                    "Marcus, because exponential growth functions eventually grow faster than positive linear functions.",
                    "Tia, because positive linear functions grow faster than exponential growth functions.",
                    "Tia, because exponential growth functions eventually grow faster than positive linear functions.",
                ],
                correct_letter="D",
                answer="(D) Tia (exponential eventually grows faster)"),
        Problem(label="4-C",
                body="Two trees were planted on the same day. The pine tree grew 4 inches per year. The maple tree started at 1 inch and doubled in height every year. After 10 years, which tree is taller?",
                options=[
                    "Pine, because positive linear functions grow faster than exponential growth functions.",
                    "Pine, because exponential growth functions eventually grow faster than positive linear functions.",
                    "Maple, because positive linear functions grow faster than exponential growth functions.",
                    "Maple, because exponential growth functions eventually grow faster than positive linear functions.",
                ],
                correct_letter="D",
                answer="(D) Maple (exponential eventually grows faster)"),
        Problem(label="4-D",
                body="A bacteria culture starts with 100 cells and increases by 50 cells per hour. A second culture starts with 10 cells and doubles every hour. After 8 hours, which culture has more cells?",
                options=[
                    "First, because positive linear functions grow faster than exponential growth functions.",
                    "First, because exponential growth functions eventually grow faster than positive linear functions.",
                    "Second, because positive linear functions grow faster than exponential growth functions.",
                    "Second, because exponential growth functions eventually grow faster than positive linear functions.",
                ],
                correct_letter="D",
                answer="(D) Second culture (exponential eventually grows faster)"),
        Problem(label="4-E",
                body="Sara started with $100 in a jar and added $50 each month. Ben started with $1 and tripled his savings each month. After 12 months, who saved more?",
                options=[
                    "Sara, because positive linear functions grow faster than exponential growth functions.",
                    "Sara, because exponential growth functions eventually grow faster than positive linear functions.",
                    "Ben, because positive linear functions grow faster than exponential growth functions.",
                    "Ben, because exponential growth functions eventually grow faster than positive linear functions.",
                ],
                correct_letter="D",
                answer="(D) Ben (exponential eventually grows faster)"),
    ],
)


TYPE_5 = ProblemType(
    number=5,
    title="Recursive Rule from a Table (MC)",
    answer_key_title="Recursive Rule from a Table",
    instruction="Find the recursive rule. Circle the correct answer.",
    layout="mc_2col",
    example_lines=[
        "Table:  n=1,2,3,4,5    f(n)=0.5, 1, 2, 4, 8",
        "First term: f(1) = 0.5.  Ratio: 1/0.5 = 2.",
        "Recursive: f(1) = 0.5, f(n) = 2 · f(n-1), n ≥ 2",
    ],
    problems=[
        Problem(label="5-A",
                body="n: 1, 2, 3, 4, 5    f(n): 0.5, 1, 2, 4, 8",
                options=[
                    "f(1) = 2, f(n) = 2 · f(n-1), n ≥ 2",
                    "f(1) = 2, f(n) = 0.5 · f(n-1), n ≥ 2",
                    "f(1) = 0.5, f(n) = 2 · f(n-1), n ≥ 2",
                    "f(1) = 0.5, f(n) = 0.5 · f(n-1), n ≥ 2",
                ],
                correct_letter="C",
                answer="(C) f(1) = 0.5, f(n) = 2 · f(n-1)"),
        Problem(label="5-B",
                body="n: 1, 2, 3, 4, 5    f(n): 3, 6, 12, 24, 48",
                options=[
                    "f(1) = 3, f(n) = 2 · f(n-1), n ≥ 2",
                    "f(1) = 2, f(n) = 3 · f(n-1), n ≥ 2",
                    "f(1) = 3, f(n) = 3 · f(n-1), n ≥ 2",
                    "f(1) = 6, f(n) = 2 · f(n-1), n ≥ 2",
                ],
                correct_letter="A",
                answer="(A) f(1) = 3, f(n) = 2 · f(n-1)"),
        Problem(label="5-C",
                body="n: 1, 2, 3, 4, 5    f(n): 100, 50, 25, 12.5, 6.25",
                options=[
                    "f(1) = 100, f(n) = 2 · f(n-1), n ≥ 2",
                    "f(1) = 100, f(n) = 0.5 · f(n-1), n ≥ 2",
                    "f(1) = 0.5, f(n) = 100 · f(n-1), n ≥ 2",
                    "f(1) = 50, f(n) = 0.5 · f(n-1), n ≥ 2",
                ],
                correct_letter="B",
                answer="(B) f(1) = 100, f(n) = 0.5 · f(n-1)"),
        Problem(label="5-D",
                body="n: 1, 2, 3, 4, 5    f(n): 4, 12, 36, 108, 324",
                options=[
                    "f(1) = 3, f(n) = 4 · f(n-1), n ≥ 2",
                    "f(1) = 4, f(n) = 4 · f(n-1), n ≥ 2",
                    "f(1) = 4, f(n) = 3 · f(n-1), n ≥ 2",
                    "f(1) = 12, f(n) = 3 · f(n-1), n ≥ 2",
                ],
                correct_letter="C",
                answer="(C) f(1) = 4, f(n) = 3 · f(n-1)"),
        Problem(label="5-E",
                body="n: 1, 2, 3, 4, 5    f(n): 5, 1, 0.2, 0.04, 0.008",
                options=[
                    "f(1) = 5, f(n) = 0.2 · f(n-1), n ≥ 2",
                    "f(1) = 0.2, f(n) = 5 · f(n-1), n ≥ 2",
                    "f(1) = 5, f(n) = 5 · f(n-1), n ≥ 2",
                    "f(1) = 1, f(n) = 0.2 · f(n-1), n ≥ 2",
                ],
                correct_letter="A",
                answer="(A) f(1) = 5, f(n) = 0.2 · f(n-1)"),
    ],
)


TYPE_6 = ProblemType(
    number=6,
    title="Classify: Arithmetic or Geometric",
    answer_key_title="Arithmetic vs. Geometric",
    instruction="Place an X in the table to show whether each sequence is arithmetic or geometric.",
    layout="table",
    table_columns=["Arithmetic", "Geometric"],
    example_lines=[
        "Sequence: 5, 9, 13, 17, 21, ...    Differences: +4 each time -> Arithmetic.",
        "Sequence: 3, 6, 12, 24, 48, ...    Ratios: x2 each time -> Geometric.",
        "Arithmetic = constant DIFFERENCE.  Geometric = constant RATIO.",
    ],
    problems=[
        Problem(label="6-A", body="78, 69, 60, 51, 42, ...", answer="Arithmetic (d = -9)"),
        Problem(label="6-B", body="4, 12, 36, 108, 324, ...", answer="Geometric (r = 3)"),
        Problem(label="6-C", body="-0.6, 0.2, 1, 1.8, 2.6, ...", answer="Arithmetic (d = +0.8)"),
        Problem(label="6-D", body="225, -22.5, 2.25, -0.225, 0.0225, ...", answer="Geometric (r = -0.1)"),
        Problem(label="6-E", body="100, 50, 25, 12.5, 6.25, ...", answer="Geometric (r = 0.5)"),
    ],
)


TYPE_7 = ProblemType(
    number=7,
    title="Common Ratio (Short Answer)",
    answer_key_title="Common Ratio",
    instruction="Find the common ratio of each sequence. Show your work.",
    layout="short_answer_right",
    example_lines=[
        "Find the common ratio of 6, 18, 54, 162, ...",
        "r = (any term) / (previous term).  18/6 = 3.  54/18 = 3.  Confirmed.",
        "Common ratio = 3.",
    ],
    problems=[
        Problem(label="7-A", body="What is the common ratio of the sequence 81, 27, 9, 3, 1, ...?",
                answer_label="r =", answer="r = 1/3"),
        Problem(label="7-B", body="What is the common ratio of the sequence 2, 6, 18, 54, ...?",
                answer_label="r =", answer="r = 3"),
        Problem(label="7-C", body="What is the common ratio of the sequence 1000, 200, 40, 8, ...?",
                answer_label="r =", answer="r = 1/5"),
        Problem(label="7-D", body="What is the common ratio of the sequence 5, -10, 20, -40, ...?",
                answer_label="r =", answer="r = -2"),
        Problem(label="7-E", body="What is the common ratio of the sequence 128, 64, 32, 16, ...?",
                answer_label="r =", answer="r = 1/2"),
    ],
)


TYPE_8 = ProblemType(
    number=8,
    title="Evaluate Exponential Function (Short Answer)",
    answer_key_title="Evaluate Exponential Function",
    instruction="Evaluate each function at the given value. Show your work.",
    layout="short_answer_right",
    example_lines=[
        "If f(x) = 256(0.5)^x, what is f(4)?",
        "Substitute x=4: f(4) = 256(0.5)^4 = 256(0.0625) = 16.",
        "Answer: f(4) = 16",
    ],
    problems=[
        Problem(label="8-A", body="If f(x) = 625(0.8)^x, what is the value of f(4)?", answer="f(4) = 256"),
        Problem(label="8-B", body="If f(x) = 3(2)^x, what is the value of f(5)?", answer="f(5) = 96"),
        Problem(label="8-C", body="If f(x) = 100(0.5)^x, what is the value of f(3)?", answer="f(3) = 12.5"),
        Problem(label="8-D", body="If f(x) = 4(3)^x, what is the value of f(4)?", answer="f(4) = 324"),
        Problem(label="8-E", body="If f(x) = 1024(0.5)^x, what is the value of f(6)?", answer="f(6) = 16"),
    ],
)


TYPE_9 = ProblemType(
    number=9,
    title="Write the Explicit Rule (Short Answer)",
    answer_key_title="Explicit Rule",
    instruction="Write the explicit rule for each geometric sequence in the form f(n) = a(r)^{n-1}.",
    layout="short_answer_below",
    example_lines=[
        "A geometric sequence has first term 23 and common ratio 7.5.",
        "Explicit rule format: f(n) = a · r^{n-1}",
        "Substitute: f(n) = 23(7.5)^{n-1}",
    ],
    problems=[
        Problem(label="9-A", body="A geometric sequence has a first term of 6 and a common ratio of 4. What is the explicit rule for this sequence?",
                answer_label="f(n) =", answer="f(n) = 6(4)^{n-1}"),
        Problem(label="9-B", body="A geometric sequence has a first term of 100 and a common ratio of 0.5. What is the explicit rule for this sequence?",
                answer_label="f(n) =", answer="f(n) = 100(0.5)^{n-1}"),
        Problem(label="9-C", body="A geometric sequence has a first term of 2 and a common ratio of 5. What is the explicit rule for this sequence?",
                answer_label="f(n) =", answer="f(n) = 2(5)^{n-1}"),
        Problem(label="9-D", body="A geometric sequence has a first term of 81 and a common ratio of 1/3. What is the explicit rule for this sequence?",
                answer_label="f(n) =", answer="f(n) = 81(1/3)^{n-1}"),
        Problem(label="9-E", body="A geometric sequence has a first term of 7 and a common ratio of 2. What is the explicit rule for this sequence?",
                answer_label="f(n) =", answer="f(n) = 7(2)^{n-1}"),
    ],
)


def main() -> None:
    worksheet = Worksheet(
        title="Exponential Functions & Geometric Sequences — Practice Worksheet",
        types=[TYPE_1, TYPE_2, TYPE_3, TYPE_4, TYPE_5, TYPE_6, TYPE_7, TYPE_8, TYPE_9],
    )
    render_worksheet(worksheet, "smoke_module13_14.pdf")
    print("Wrote smoke_module13_14.pdf")


if __name__ == "__main__":
    main()
