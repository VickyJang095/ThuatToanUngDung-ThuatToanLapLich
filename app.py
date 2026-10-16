from flask import Flask

from scheduling.branch_and_bound import branch_and_bound
from scheduling.genetic import (
    crossover,
    decode_permutation,
    genetic_algorithm,
    mutate,
    random_permutation,
)
from scheduling.greedy import greedy_schedule, schedule_lpt
from scheduling.jobs import random_jobs
from scheduling.metrics import evaluate_schedule
from scheduling.service import run_algorithms, serialize_schedule
from web.routes import web


app = Flask(__name__)
app.register_blueprint(web)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)