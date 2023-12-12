from neo4j import GraphDatabase as gd
import neo4j.exceptions
import psycopg2 as pg
from sklearn.cluster import KMeans

postgres_conn = None

def query_1():
    '''
    1. User inputs a country, city, sector, and then their order of importance 1-7 for each of the following:
        - opportunities_ranking
        - comp_benefits_ranking
        - culture_values_ranking
        - senior_management_ranking
        - worklife_balance_ranking
        - ceo_approval_ranking
        - company_outlook_ranking

    2. Values of the user's preferences comes from the frontend, with which we construct a pseudo-review node.

    3. We then use the cosine similarity algorithm to find the most 10 most similar reviews to the pseudo-review.

    4. We then return the top 10 jobs associated with those reviews.
    '''

    # Configure Neo4J Connection
    driver = gd.driver("neo4j://localhost:7687", auth=("neo4j", "hello"))
    try:
        driver.verify_connectivity()
    except neo4j.exceptions.ServiceUnavailable:
        print('Connection to Neo4j database failed. Please try again.')
        exit()

    # Neo4J similarity construction
    neo_similarity_query = """
        WITH $job_review_preferences AS job_review_preferences
        MATCH (r:Review)
        WITH r, job_review_preferences,
            [
                r.opportunities_rank,
                r.comp_benefits_rank,
                r.culture_values_rank,
                r.senior_management_rank,
                r.worklife_balance_rank,
                r.ceo_approval_rank,
                r.company_outlook_rank
            ] AS job_review_ranks
        WITH r, gds.similarity.cosine(job_review_preferences, job_review_ranks) AS similarity
        RETURN r.review_id AS reviewId, similarity AS cosineSimilarity
        ORDER BY similarity DESC
        LIMIT 10
        """

    with driver.session() as session:
        # Grab relevant jobs with user scores
        demo_job_review_preferences = [3, 5, 7, 2, 1, 6, 4]
        result = session.run(neo_similarity_query, job_review_preferences=demo_job_review_preferences)
        jobs = [job for job in result]

    # try:
    #         # Configure PostgreSQL connection
    #     postgres_conn = pg.connect(
    #         host="s-l112.engr.uiowa.edu",
    #         port=5432,
    #         database="mdb_student18",
    #         user='mdb_student18',
    #         password='finalproject2023')
    #     cur = postgres_conn.cursor()

    # except (Exception, pg.DatabaseError) as error:
    #     print(error)
    # finally:
    #     if postgres_conn is not None:
    #         postgres_conn.close()
    return

'''
2. [Neo4J] We will cluster companies around countries/cities, and allow the user to query a city or company and return the other
companies in the cluster. Hoping to add a feature that allows the user to search for certain keywords in employee reviews as well.
'''
def cluster_reviews(song_features, num_clusters=3):
    # Cluster the songs
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(song_features)
    centroids = kmeans.cluster_centers_
    return centroids

def query_2():
    return


query_1()


'''
MATCH (c:Company)
WITH [c.benefits_rating] AS swag
SET c.br_graph = swag
RETURN count(c)

CALL gds.graph.project(
    'company_graph',
    {
        Company: {
            properties: 'br_graph'
        }
    },
    '*'
)

CALL gds.kmeans.write.estimate('company_graph', {
    writeProperty: 'br_graph',
    nodeProperty: 'benefits_rating'
})
YIELD nodeCount, bytesMin, bytesMax, requiredMemory

CALL gds.kmeans.write('company_graph', {
    writeProperty: 'kmeans',
    nodeProperty: 'br_graph',
    k: 3,
    randomSeed: 42
})
YIELD nodePropertiesWritten
'''