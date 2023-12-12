import os

from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS

from neo4j_db import get_neo4j_db, get_similar_jobs, get_companies_in_cluster
from postgres_db import get_postgres_db, get_all_job_info

# Load .env file
load_dotenv()

# Now you can use os.environ to get your environment variables
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

NEO4J_URI = os.environ.get('NEO4J_URI')
NEO4J_USER = os.environ.get('NEO4J_USER')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')

app = Flask(__name__)
CORS(app)

postgres_db = get_postgres_db(POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD)
neo4j_db = get_neo4j_db(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)


@app.route('/countries/distinct', methods=['GET'])
def countries_distinct():
    cursor = postgres_db.cursor()
    cursor.execute(
        """
        SELECT LOWER(country)
        FROM final_project.job
        GROUP BY LOWER(country)
        HAVING COUNT(*) > 100;
        """
    )
    countries = cursor.fetchall()
    return [country[0] for country in countries]


@app.route('/cities/distinct/<country>', methods=['GET'])
def cities_distinct(country):
    cursor = postgres_db.cursor()
    cursor.execute(
        """
        SELECT LOWER(city)
        FROM final_project.job
        WHERE
            LOWER(country) = LOWER(%s)
        GROUP BY LOWER(city)
        HAVING COUNT(DISTINCT sector) > 1;
        """,
        (country,)
    )
    cities = cursor.fetchall()
    return [city[0] for city in cities]


@app.route('/sectors/distinct/<country>/<city>', methods=['GET'])
def sectors_distinct(country, city):
    if city == 'null':
        cursor = postgres_db.cursor()
        cursor.execute(
            """
            SELECT LOWER(sector)
            FROM final_project.job
            WHERE
                LOWER(country) = LOWER(%s)
            GROUP BY LOWER(sector);
            """,
            (country,)
        )
        sectors = cursor.fetchall()
    else:
        cursor = postgres_db.cursor()
        cursor.execute(
            """
            SELECT LOWER(sector)
            FROM final_project.job
            WHERE
                LOWER(country) = LOWER(%s) AND
                LOWER(city) = LOWER(%s)
            GROUP BY LOWER(sector);
            """,
            (country, city)
        )
        sectors = cursor.fetchall()
    return [sector[0] for sector in sectors]


@app.route('/similarly/ranked/jobs', methods=['POST'])
def similar_ranks():
    data = request.json
    country = data['country']
    city = data['city']
    sector = data['sector']
    ranks = [
        data['ranks']['opportunities_ranking'],
        data['ranks']['comp_benefits_ranking'],
        data['ranks']['culture_values_ranking'],
        data['ranks']['senior_management_ranking'],
        data['ranks']['worklife_balance_ranking'],
        data['ranks']['ceo_approval_ranking'],
        data['ranks']['company_outlook_ranking']
    ]

    result = get_similar_jobs(neo4j_db, country, city, sector, ranks)
    review_ids = []
    for review_id in result:
        review_ids.append(review_id)

    resp = []
    jobs = get_all_job_info(postgres_db, review_ids)
    for i in review_ids:
        for job in jobs:
            if i == job[0]:
                resp.append({
                    'job_id': job[1],
                    'job_title': job[2],
                    'company_name': job[3],
                    'company_size': job[4],
                    'salary_type': job[5],
                    'ten_percentile_salary': job[6],
                    'fifty_percentile_salary': job[7],
                    'ninety_percentile_salary': job[8]
                })
    return {'jobs': resp}


@app.route('/company/<country>/<city>/<sector>', methods=['GET'])
def get_companies(country, city, sector):
    cursor = postgres_db.cursor()
    cursor.execute(
        """
        SELECT
            c.id,
            c.name,
            c.size,
            c.benefits_rating
        FROM final_project.company c
        WHERE c.id IN (
            SELECT DISTINCT j.company_id
            FROM final_project.job j
            WHERE
                LOWER(j.country) = LOWER(%s) AND
                LOWER(j.city) = LOWER(%s) AND
                LOWER(j.sector) = LOWER(%s)
        );
        """, (country, city, sector)
    )
    results = cursor.fetchall()
    companies = []
    for result in results:
        companies.append({
            'id': result[0],
            'name': result[1],
            'size': result[2],
            'benefits_rating': result[3]
        })
    return {'companies': companies}


@app.route('/similar/companies/<company_id>/<country>/<city>', methods=['GET'])
def similar_companies(company_id, country, city):
    company_ids = get_companies_in_cluster(neo4j_db, company_id)
    cursor = postgres_db.cursor()
    cursor.execute(
        """
        SELECT
            c.id,
            c.name,
            c.size,
            c.benefits_rating
        FROM final_project.company c
        WHERE
            c.id = ANY(%s) AND
            c.id IN (
                SELECT DISTINCT j.company_id
                FROM final_project.job j
                WHERE
                    LOWER(j.country) = LOWER(%s) AND
                    LOWER(j.city) = LOWER(%s)
                    );
        """, (company_ids, country, city)
    )
    results = cursor.fetchall()
    companies = []
    for result in results:
        companies.append({
            'id': result[0],
            'name': result[1],
            'size': result[2],
            'benefits_rating': result[3]
        })
    return {'companies': companies}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
