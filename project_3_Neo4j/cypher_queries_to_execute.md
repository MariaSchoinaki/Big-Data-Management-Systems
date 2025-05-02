# Step 4: Write and Benchmark Queries

Once the data is loaded, you can execute the following Cypher queries to analyze the graph:

## Show a Small Portion of the Graph

```cypher
MATCH (u:User)-[r:PERFORMS]->(t:Target)
RETURN u, r, t
LIMIT 25
```

## Count All Users

```cypher
MATCH (u:User)
RETURN COUNT(u) AS user_count
```

## Count All Targets

```cypher
MATCH (t:Target)
RETURN COUNT(t) AS target_count
```

## Count All Actions

```cypher
MATCH ()-[r:PERFORMS]->()
RETURN COUNT(r) AS action_count
```

## Show Actions and Targets of a Specific User

```cypher
MATCH (u:User {id: 'user_123'})-[r:PERFORMS]->(t:Target)
RETURN r.action_id, t.id
```

## Count Actions per User

```cypher
MATCH (u:User)-[r:PERFORMS]->()
RETURN u.id, COUNT(r) AS action_count
```

## Count Users per Target

```cypher
MATCH ()-[r:PERFORMS]->(t:Target)
RETURN t.id, COUNT(DISTINCT r) AS user_count
```

## Average Actions per User

```cypher
MATCH (u:User)-[r:PERFORMS]->()
RETURN AVG(SIZE((u)-[:PERFORMS]->())) AS avg_actions_per_user
```

## Users and Targets with Positive Feature2

```cypher
MATCH (u:User)-[r:PERFORMS]->(t:Target)
WHERE r.feature2 > 0
RETURN u.id, t.id
```

## Count Actions with Label "1" per Target

```cypher
MATCH ()-[r:PERFORMS]->(t:Target)
WHERE r.label = 1
RETURN t.id, COUNT(r) AS positive_label_count
```
