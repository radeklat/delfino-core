from delfino_core.commands.typecheck import typecheck


class TestTypecheckCommand:
    @staticmethod
    def should_log_header(runner, context_obj):
        result = runner.invoke(typecheck, obj=context_obj)
        assert "RUNNING TYPE CHECKER" in result.output
