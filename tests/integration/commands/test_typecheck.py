from delfino_core.commands.typecheck import run_mypy


class TestTypecheckCommand:
    @staticmethod
    def test_should_log_progress(runner, context_obj):
        result = runner.invoke(run_mypy, obj=context_obj)
        assert "mypy" in result.output
