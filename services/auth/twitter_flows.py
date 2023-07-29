import enum


class TwitterAuthFlows(enum.Enum, str):
    INIT_AUTH = 'InitAuth'
    LOGIN_JS_INSTRUMENTATION_SUBTASK = 'LoginJsInstrumentationSubtask'
    LOGIN_ENTER_USER_IDENTIFIER_SSO = 'LoginEnterUserIdentifierSSO'
    LOGIN_ENTER_ALTERNATE_IDENTIFIER = 'LoginEnterAlternateIdentifierSubtask'
    LOGIN_ENTER_PASSWORD = 'LoginEnterPassword'
    ACCOUNT_DUPLICATION_CHECK = 'AccountDuplicationCheck'
    SUCCESS_EXIT = 'SuccessExit'
    FAILURE_EXIT = 'FailureExit'
