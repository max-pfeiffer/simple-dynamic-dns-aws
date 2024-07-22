FROM public.ecr.aws/lambda/python:3.12

RUN pip install poetry==1.8.3 && poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock ./lambda/lambda_function.py ${LAMBDA_TASK_ROOT}

RUN poetry install --no-interaction --without dev

CMD [ "lambda_function.lambda_handler" ]
