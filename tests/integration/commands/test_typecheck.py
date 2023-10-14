from delfino_core.commands.typecheck import run_mypy


class TestTypecheckCommand:
    @staticmethod
    def should_log_header(runner, context_obj):
        result = runner.invoke(run_mypy, obj=context_obj)
        assert "RUNNING TYPE CHECKER" in result.output
