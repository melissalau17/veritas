import json

from src.ingest import (
    load_documents,
    build_context,
)

from src.retrieval import (
    retrieve_documents,
)

from src.verifier import (
    find_revision_conflicts,
)

from src.meta_client import (
    ask_muse,
    model_is_configured,
)


def build_investigation_prompt(
    problem,
    evidence,
    conflicts,
):
    """
    Build the prompt supplied to Muse.
    """

    evidence_context = (
        build_context(
            evidence
        )
    )

    conflict_context = (
        json.dumps(
            conflicts,
            indent=2
        )
    )

    return f"""
ENGINEERING PROBLEM
===================

{problem}


RETRIEVED ENGINEERING EVIDENCE
==============================

{evidence_context}


DETERMINISTIC VERIFICATION RESULTS
==================================

{conflict_context}


YOUR TASK
=========

Analyze the engineering problem using ONLY
the supplied evidence.

Produce these sections:

## Observed Condition

Describe only what is known from the
problem statement and evidence.

## Relevant Historical Evidence

Identify relevant previous incidents or
maintenance work.

## Revision and Applicability Verification

Explain whether referenced procedures are
current or superseded.

## Conflicts and Warnings

Explain conflicts between sources,
including changed technical requirements.

## Recommended Investigation Steps

Recommend what the HUMAN ENGINEER should
investigate next.

Do not authorize repairs or claim a final
root cause.

## Uncertainty / Missing Information

State what measurements, inspections, or
information are still missing.

## Sources

List the filenames actually used.

IMPORTANT:

Every important factual claim must reference
a supplied source filename.

Never invent information that does not exist
in the supplied evidence.
""".strip()


def build_fallback_answer(
    problem,
    conflicts
):
    """
    Provide useful output when Muse hasn't
    been connected yet.
    """

    lines = [
        "### Observed Condition",
        "",
        problem,
        "",
    ]

    if conflicts:

        lines.extend(
            [
                "### Revision Verification",
                "",
            ]
        )

        for conflict in conflicts:

            message = (
                f"- **{conflict['source']}** "
                f"references "
                f"**{conflict['document_id']} "
                f"Revision "
                f"{conflict['referenced_revision']}**, "
                f"but the current revision is "
                f"**Revision "
                f"{conflict['current_revision']}**."
            )

            lines.append(message)

            if (
                conflict[
                    "old_tolerance"
                ]
                and conflict[
                    "current_tolerance"
                ]
            ):

                lines.append(
                    (
                        f"  - Historical tolerance: "
                        f"{conflict['old_tolerance']}"
                    )
                )

                lines.append(
                    (
                        f"  - Current tolerance: "
                        f"{conflict['current_tolerance']}"
                    )
                )

        lines.extend(
            [
                "",
                "### Investigation Direction",
                "",
                (
                    "The historical case may be "
                    "relevant, but the engineer "
                    "should evaluate the current "
                    "condition using the current "
                    "approved procedure rather "
                    "than the superseded revision."
                ),
                "",
                (
                    "No root cause has been "
                    "confirmed."
                ),
            ]
        )

    else:

        lines.extend(
            [
                "### Verification Result",
                "",
                (
                    "No revision conflict was "
                    "detected by the deterministic "
                    "verification layer."
                ),
            ]
        )

    return "\n".join(lines)


def investigate(
    problem,
    data_dir=None,
    top_k=5,
):
    """
    Complete Veritas investigation workflow.
    """

    documents = load_documents(
        data_dir
    )

    evidence = (
        retrieve_documents(
            query=problem,
            documents=documents,
            top_k=top_k,
        )
    )

    conflicts = (
        find_revision_conflicts(
            documents
        )
    )

    model_answer = None

    model_error = None

    if model_is_configured():

        prompt = (
            build_investigation_prompt(
                problem=problem,
                evidence=evidence,
                conflicts=conflicts,
            )
        )

        try:

            model_answer = (
                ask_muse(
                    prompt
                )
            )

        except Exception as error:

            model_error = str(
                error
            )

    if model_answer:

        recommendation = (
            model_answer
        )

        used_model = True

    else:

        recommendation = (
            build_fallback_answer(
                problem,
                conflicts,
            )
        )

        used_model = False

    return {
        "problem":
            problem,

        "documents":
            documents,

        "evidence":
            evidence,

        "conflicts":
            conflicts,

        "recommendation":
            recommendation,

        "used_model":
            used_model,

        "model_error":
            model_error,
    }


if __name__ == "__main__":

    test_problem = (
        "Pump P-101 has abnormal vibration "
        "after its coupling was replaced. "
        "What should the engineer investigate?"
    )

    result = investigate(
        test_problem
    )

    print(
        "\n======================"
    )

    print(
        "VERIMAINT INVESTIGATION"
    )

    print(
        "======================\n"
    )

    print(
        result[
            "recommendation"
        ]
    )

    print(
        "\nModel used:",
        result["used_model"]
    )

    if result[
        "model_error"
    ]:

        print(
            "\nModel error:"
        )

        print(
            result[
                "model_error"
            ]
        )