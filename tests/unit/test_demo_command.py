from delfino_core import demo


class TestDemoCommand:
    @staticmethod
    def should_log_demo_message(runner):
        result = runner.invoke(demo)
        assert result.exit_code == 0
        assert result.output == "This is a demo plugin.\n"
