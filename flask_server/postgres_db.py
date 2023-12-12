import psycopg2


def get_postgres_db(host, user, password):
    return psycopg2.connect(
        host=host,
        database=user,
        user=user,
        password=password
    )


def get_all_job_info(postgres_db, review_ids):
    cursor = postgres_db.cursor()
    cursor.execute(
        """
        SELECT
            r.id,
            j.id,
            j.job_title,
            c.name,
            c.size,
            s.salary_type,
            s.ten_percentile_salary,
            s.fifty_percentile_salary,
            s.ninety_percentile_salary
        FROM
            final_project.review r
            JOIN final_project.job j ON j.review_id = r.id
            JOIN final_project.company c ON c.id = r.company_id
            JOIN final_project.salary s ON j.salary_id = s.salary_id
        WHERE
            r.id = ANY(%s)
        """,
        (review_ids,)
    )
    results = cursor.fetchall()
    return results
