from .exceptions import (
    BaseError,
    InternalServerError,
    MethodNotAllowed,
    NotFound,
    StatusCode,
    Unauthorized
)


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_):
        return NotFound().to_response()

    @app.errorhandler(405)
    def not_allowed(_):
        return MethodNotAllowed().to_response()

    @app.errorhandler(BaseError)
    def handle_error(error: BaseError):
        from main.libs.log import ServiceLogger

        logger = ServiceLogger(__name__)

        status_code = error.status_code
        if (
                isinstance(status_code, int)
                and status_code != StatusCode.INTERNAL_SERVER_ERROR
        ):
            logging_method = logger.warning
        else:
            logging_method = logger.error

        logging_method(
            message=error.error_message,
            data={
                "error_data": error.error_data,
                "error_code": error.error_code,
            },
        )
        return error.to_response()

    @app.errorhandler(Exception)
    def handle_exception(e):
        from main.libs.log import ServiceLogger

        logger = ServiceLogger(__name__)
        logger.exception(message=str(e))

        return InternalServerError(error_message=str(e)).to_response()


def register_jwt_error_handler(jwt):
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        response = Unauthorized()
        response.error_data = {"access_token": "Expired access token"}
        return response.to_response()

    @jwt.unauthorized_loader
    def unauthorized_loader_callback(message):
        response = Unauthorized()
        response.error_data = {"access_token": message}
        return response.to_response()
