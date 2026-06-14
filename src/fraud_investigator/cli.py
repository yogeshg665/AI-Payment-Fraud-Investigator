"""Command-line interface for the AI Payment Fraud Investigator."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from fraud_investigator.models.decision import DecisionOutcome
from fraud_investigator.pipeline.investigation_pipeline import (
    InvestigationPipeline,
    load_cases_from_json,
)
from fraud_investigator.utils.config import load_config

app = typer.Typer(
    add_completion=False,
    help="Automated payment fraud investigation engine.",
)
console = Console()

_OUTCOME_STYLE = {
    DecisionOutcome.APPROVE.value: "green",
    DecisionOutcome.ESCALATE.value: "yellow",
    DecisionOutcome.DECLINE.value: "red",
}


@app.command()
def investigate(
    input_file: Path = typer.Argument(..., help="Path to a JSON file of case inputs."),
    config_file: Path = typer.Option(None, "--config", "-c", help="Path to config.yaml."),
    output_dir: Path = typer.Option(None, "--output", "-o", help="Directory for reports."),
) -> None:
    """Investigate one or more transactions from a JSON input file."""
    load_dotenv()
    config = load_config(config_file)
    pipeline = InvestigationPipeline(config=config)

    cases = load_cases_from_json(input_file)
    results = pipeline.run_batch(cases, output_dir=output_dir)

    table = Table(title="Investigation Results")
    table.add_column("Case ID", style="cyan", no_wrap=True)
    table.add_column("Transaction", style="white")
    table.add_column("Risk", justify="right")
    table.add_column("Decision", justify="center")
    table.add_column("Confidence", justify="right")

    for result in results:
        decision = result.decision
        style = _OUTCOME_STYLE.get(decision.outcome.value, "white")
        table.add_row(
            decision.case_id,
            result.report["transaction"]["transaction_id"],
            f"{decision.risk_score:.1f}",
            f"[{style}]{decision.outcome.value.upper()}[/{style}]",
            f"{decision.confidence:.0%}",
        )

    console.print(table)
    if output_dir:
        console.print(f"Reports written to [bold]{output_dir}[/bold].")


@app.command()
def explain(
    input_file: Path = typer.Argument(..., help="Path to a JSON file with a single case."),
    config_file: Path = typer.Option(None, "--config", "-c", help="Path to config.yaml."),
) -> None:
    """Investigate the first case in a file and print its full narrative report."""
    load_dotenv()
    config = load_config(config_file)
    pipeline = InvestigationPipeline(config=config)

    cases = load_cases_from_json(input_file)
    if not cases:
        console.print("[red]No cases found in input file.[/red]")
        raise typer.Exit(code=1)

    result = pipeline.run_one(cases[0])
    console.print_json(json.dumps(result.report))


if __name__ == "__main__":
    app()
