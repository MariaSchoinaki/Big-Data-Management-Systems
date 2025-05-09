## Big Data Management Systems - 2nd Project 2025: MongoDB Aggregation

> Maria Schoinaki, BSc Student <br />
> Department of Informatics, Athens University of Economics and Business <br />
> p3210191@aueb.gr <br/><br/>

> Nikos Mitsakis, BSc Student <br />
> Department of Informatics, Athens University of Economics and Business <br />
> p3210122@aueb.gr <br/><br/>

Below is the write-up template with each question, the exact command used, the observed output, and space for a short explanatory comment when needed. We ran the queries in both our machines and had slighlty different results (seed).

---

### Preparation

1. **Load data**:

   ```js
   use studentsDB
    load("C:\\Users\\mitsa\\Desktop\\8th_Semester\\Big_Data_Management_Systems\\PROJECTS\\DBMS-Projects\\project_2_MongoDB\\data\\prep.js")
   ```

   **Output**: `true` (multiple records inserted)

2. **Verify data**:

   ```js
   db.students.findOne()
   ```

   **Output**:

   ```json
    {
      _id: ObjectId('681079c8a9ee5b8ed4b5f899'),        
      home_city: 'Ioannina',
      first_name: 'Nikos',
     /* ... */
    }
   ```
---

## Question 1: Count students with any “In Progress” class

**Command**:

```js
db.students.countDocuments({
...   "courses.course_status": "In Progress"
... })
```

**Output**:

```
8833
```

---

## Question 2: Number of students per home city

**Command**:

```js
db.students.aggregate([
...   {
...     $group: {
...       _id: "$home_city",
...       number_of_students: { $sum: 1 }
...     }
...   }
... ])
```

**Output (top 5)**:

```
[ { _id: 'Patra', number_of_students: 504 },
  { _id: 'Preveza', number_of_students: 491 },
  { _id: 'Kalamata', number_of_students: 449 },
  { _id: 'Arta', number_of_students: 488 },
  { _id: 'Pyrgos', number_of_students: 509 } ]
```

---

## Question 3: Most popular hobby(ies)

**Command**:

```js
db.students.aggregate([
...   { $unwind: "$hobbies" },
...   { $group: { _id: "$hobbies", count: { $sum: 1 } } },
...   { $sort: { count: -1 } },
...   { $limit: 1 }
... ])
```

**Output**:

```json
[ { _id: 'guitar', count: 1305 } ]
```

**Comment**: We `$unwind` the hobbies array to count each hobby occurrence individually, then `$group` by hobby to sum counts, and finally filter on the top count to output only the most popular hobby(ies).

---

## Question 4: GPA of the top student

**Command**:

```js
db.students.aggregate([
...   {
...     $addFields: {
...       tens: {
...         $size: {
...           $filter: {
...             input: "$courses",
...             as: "course",
...             cond: { $eq: ["$$course.grade", 10] }
...           }
...         }
...       }
...     }
...   },
...   { $sort: { tens: -1 } },
...   { $limit: 1 },
...   {
...     $project: {
...       first_name: 1,
...       tens: 1
...     }
...   }
... ])
```

**Output**:

```json
  [ {
    _id: ObjectId('681079c8a9ee5b8ed4b5f89c'),
    first_name: 'Eleni',
    gpa: 10
  } ]
```

---

## Question 5: Student with most grade-10’s

**Command**:

```js
db.students.aggregate([
...   {
...     $addFields: {
...       tens: {
...         $size: {
...           $filter: {
...             input: "$courses",
...             as: "course",
...             cond: { $eq: ["$$course.grade", 10] }
...           }
...         }
...       }
...     }
...   },
...   { $sort: { tens: -1 } },
...   { $limit: 1 },
...   {
...     $project: {
...       first_name: 1,
...       tens: 1
...     }
...   }
... ])
... 
```

**Output**:

```json
[
  {
    _id: ObjectId('681079d2a9ee5b8ed4b60ae1'),
    first_name: 'Clio',
    tens: 6
  }
]
```

---

## Question 6: Class with highest average GPA

**Command**:

```js
db.students.aggregate([
...   { $unwind: "$courses" },
...   {
...     $match: {
...       "courses.course_status": "Complete"
...     }
...   },
...   {
...     $group: {
...       _id: "$courses.course_title",
...       avg_grade: { $avg: "$courses.grade" }
...     }
...   },
...   { $sort: { avg_grade: -1 } },
...   { $limit: 1 }
... ])
```

**Output**:

```json
[
  {
    _id: 'Algorithms and Data Structures',
    avg_grade: 7.813975448536355
  }
]
```

---

## Question 7: Class dropped most often

**Command**:

```js
db.students.aggregate([
...   { $unwind: "$courses" },
...   {
...     $match: {
...       "courses.course_status": "Dropped"
...     }
...   },
...   {
...     $group: {
...       _id: "$courses.course_title",
...       drops: { $sum: 1 }
...     }
...   },
...   { $sort: { drops: -1 } },
...   { $limit: 1 }
... ])
```

**Output**:

```json
[ { _id: 'Algorithms and Data Structures', drops: 244 } ]
```

---

## Question 8: Completed classes by type

**Command**:

```js
db.students.aggregate([
...   { $unwind: "$courses" },
...   {
...     $match: {
...       "courses.course_status": "Complete"
...     }
...   },
...   {
...     $group: {
...       _id: { $substrBytes: ["$courses.course_code", 0, 1] },
...       count: { $sum: 1 }
...     }
...   },
...   { $sort: { count: -1 } }
... ])
```

**Output**:

```json
[
  { _id: 'P', count: 6756 },
  { _id: 'M', count: 4483 },
  { _id: 'S', count: 4376 },
  { _id: 'D', count: 3287 },
  { _id: 'V', count: 2274 },
  { _id: 'B', count: 1111 }
]
```

---

## Question 9: Add `hobbyist` boolean field

**Command**:

```js
db.students.aggregate([
...   {
...     $addFields: {
...       hobbyist: {
...         $gt: [ { $size: "$hobbies" }, 3 ]
...       }
...     }
...   },
...   {
...     $project: {
...       first_name: 1,
...       hobbies: 1,
...       hobbyist: 1
...     }
...   }
... ])
```

**Output (sample)**:

```json
[
  {
    _id: ObjectId('681079c8a9ee5b8ed4b5f899'),
    first_name: 'Nikos',
    hobbies: [ 'cinema', 'skydiving', 'guitar', 'poetry' ],
    hobbyist: true
  },
  {
    _id: ObjectId('681079c8a9ee5b8ed4b5f89a'),
    first_name: 'Despoina',
    hobbies: [ 'archaeology', 'board games' ],
    hobbyist: false
  },
 /* ... */
 ]
```

---

## Question 10: Add `completedClasses` count field

**Command**:

```js
db.students.aggregate([
...   {
...     $addFields: {
...       completed_classes: {
...         $size: {
...           $filter: {
...             input: "$courses",
...             as: "course",
...             cond: { $eq: ["$$course.course_status", "Complete"] }
...           }
...         }
...       }
...     }
...   },
...   {
...     $project: {
...       first_name: 1,
...       completed_classes: 1
...     }
...   }
... ])
```

**Output (sample)**:

```json
[
  {
    _id: ObjectId('681079c8a9ee5b8ed4b5f899'),
    first_name: 'Nikos',
    completed_classes: 3
  },
  {
    _id: ObjectId('681079c8a9ee5b8ed4b5f89a'),
    first_name: 'Despoina',
    completed_classes: 1
  },
 /* ... */
]
```

---

## Question 11: Final reshape

No other fields should remain—only `_id`, `first_name`, `GPA`, `classesInProgress`, `droppedClasses`.

**Command**:

```js
db.students.aggregate([
...   {
...     $addFields: {
...       GPA: {
...         $avg: {
...           $map: {
...             input: {
...               $filter: {
...                 input: "$courses",
...                 as: "course",
...                 cond: { $eq: ["$$course.course_status", "Complete"] }
...               }
...             },
...             as: "completedCourse",
...             in: "$$completedCourse.grade"
...           }
...         }
...       },
...       classesInProgress: {
...         $size: {
...           $filter: {
...             input: "$courses",
...             as: "course",
...             cond: { $eq: ["$$course.course_status", "In Progress"] }
...           }
...         }
...       },
...       droppedClasses: {
...         $size: {
...           $filter: {
...             input: "$courses",
...             as: "course",
...             cond: { $eq: ["$$course.course_status", "Dropped"] }
...           }
...         }
...       }
...     }
...   },
...   {
...     $project: {
...       first_name: 1,
...       GPA: 1,
...       classesInProgress: 1,
...       droppedClasses: 1
...     }
...   }
... ])
```

**Output (sample)**:

```json
[
  {
    _id: ObjectId('681079c8a9ee5b8ed4b5f899'),
    first_name: 'Nikos',
    GPA: 8,
    classesInProgress: 1,
    droppedClasses: 0
  },
  {
    _id: ObjectId('681079c8a9ee5b8ed4b5f89a'),
    first_name: 'Despoina',
    GPA: 4,
    classesInProgress: 1,
    droppedClasses: 1
  }, 
  /* ... */
]
```

---

### Final Notes
* Seed Variability: prep.js uses a random seed to generate the students collection, so numeric results (e.g., counts, GPA, most popular hobby) will differ slightly each time.

* The GPA stage uses a `$cond` to avoid division by zero, returning `null` when no completed courses exist.


---

## Appendix

### Appendix A: Mitsas’s raw log excerpt

```text
PS C:/Users/mitsa/Desktop/8th_Semester/Big_Data_Management_Systems/PROJECTS/DBMS-Projects/project_2_MongoDB> mongosh
Current Mongosh Log ID: 68107919a9ee5b8ed4b5f898
Connecting to:          mongodb://127.0.0.1:27017/?...
test> use studentsDB
```

### Appendix B: Shina’s raw log excerpt

```text
PS C:/Program Files/MongoDB/mongosh-2.5.1-win32-x64/bin> ./mongosh.exe
Current Mongosh Log ID: 681b4d0ac16edfdcde6c4bcf
Connecting to:          mongodb://127.0.0.1:27017/?...
test> use studentsDB
```
