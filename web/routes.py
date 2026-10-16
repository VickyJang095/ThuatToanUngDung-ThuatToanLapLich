from flask import Blueprint, jsonify, render_template, request

from scheduling.jobs import random_jobs
from scheduling.service import run_algorithms


web = Blueprint("web", __name__)


@web.route("/")
def home():
    return render_template("index.html")


@web.route("/api/generate", methods=["POST"])
def generate_jobs_api():
    data = request.get_json(force=True)
    machine_count = int(data.get("machines", 3))
    job_count = int(data.get("jobs", 10))
    try:
        jobs = random_jobs(job_count, machines=machine_count,
                           deadline_level=data.get("deadline_level", "medium"))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"machines": machine_count, "jobs": jobs})


@web.route("/api/run", methods=["POST"])
def run_algorithms_api():
    data = request.get_json(force=True)
    machine_count = int(data.get("machines", 3))
    jobs = data.get("jobs", [])
    pop_size = int(data.get("population", 60))
    generations = int(data.get("generations", 120))
    crossover_rate = float(data.get("crossover", 0.8))
    mutation_rate = float(data.get("mutation", 0.1))
    jobs_count = int(data.get("jobs_count", 10)) if not jobs else 10
    if not jobs:
        try:
            jobs = random_jobs(jobs_count, machines=machine_count,
                               deadline_level=data.get("deadline_level", "medium"))
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    return jsonify(run_algorithms(
        machine_count,
        jobs,
        pop_size=pop_size,
        generations=generations,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        jobs_count=jobs_count,
    ))