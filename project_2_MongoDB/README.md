# Project 2 - MongoDB / Document Stores

## Project Description

This project involves creating a MongoDB collection of student data, performing aggregation queries, and transforming the documents according to specific requirements. The data was loaded from a randomized JavaScript file (`prep.js`) that created a large collection (`students`) with ~10,000 entries.

---

## Setup and Environment

### Installed Software and Tools

- **MongoDB Community Server 8.0.8**
- **MongoDB Shell (mongosh) 2.5.0**
- **MongoDB Compass** (for GUI-based visualization)
- **Visual Studio Code** (with MongoDB extension)

### Operating System

- Windows 10

### Steps Taken

1. Installed MongoDB Community Server.
2. Installed MongoDB Shell (mongosh) separately.
3. Added necessary paths to the system PATH variable.
4. Started MongoDB service.
5. Verified successful connection using `mongosh`.
6. Loaded `prep.js` into a new database `studentsDB`.

---

## Tasks Completed

### 1. Load Data

**Command Typed:**

```javascript
use studentsDB
load("C:\\Users\\mitsa\\Desktop\\8th_Semester\\Big_Data_Management_Systems\\PROJECTS\\DBMS-Projects\\project_2_MongoDB\\data\\prep.js")
```

**Output:**

- DeprecationWarning about `insert()`, but data loaded successfully.
- Verified with:

```javascript
db.students.findOne()
```

### 2. Count Students Currently Taking Classes

**Command Typed:**

```javascript
db.students.countDocuments({ "courses.course_status": "In Progress" })
```

**Output:** 8833 students

### 3. Count Students with Completed Classes

**Command Typed:**

```javascript
db.students.countDocuments({ "courses.course_status": "Complete" })
```

**Output:** 9373 students

### 4. Group Students by Home City

**Command Typed:**

```javascript
db.students.aggregate([
  { $group: { _id: "$home_city", number_of_students: { $sum: 1 } } }
])
```

**Output:** List of cities with student counts

### 5. Find Most Popular Hobby

**Command Typed:**

```javascript
db.students.aggregate([
  { $unwind: "$hobbies" },
  { $group: { _id: "$hobbies", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 1 }
])
```

**Output:** 'guitar' with 1305 occurrences

### 6. Find GPA of the Best Student

**Command Typed:**

```javascript
db.students.aggregate([
  {
    $addFields: {
      gpa: {
        $avg: {
          $map: {
            input: {
              $filter: {
                input: "$courses",
                as: "course",
                cond: { $eq: ["$$course.course_status", "Complete"] }
              }
            },
            as: "completedCourse",
            in: "$$completedCourse.grade"
          }
        }
      }
    }
  },
  { $sort: { gpa: -1 } },
  { $limit: 1 },
  { $project: { first_name: 1, gpa: 1 } }
])
```

**Output:** Eleni with GPA = 10

### 7. Find Student with Most Grade 10's

**Command Typed:**

```javascript
db.students.aggregate([
  {
    $addFields: {
      tens: {
        $size: {
          $filter: {
            input: "$courses",
            as: "course",
            cond: { $eq: ["$$course.grade", 10] }
          }
        }
      }
    }
  },
  { $sort: { tens: -1 } },
  { $limit: 1 },
  { $project: { first_name: 1, tens: 1 } }
])
```

**Output:** Clio with 6 grade 10's

### 8. Find Class with Highest Average GPA

**Command Typed:**

```javascript
db.students.aggregate([
  { $unwind: "$courses" },
  { $match: { "courses.course_status": "Complete" } },
  { $group: { _id: "$courses.course_title", avg_grade: { $avg: "$courses.grade" } } },
  { $sort: { avg_grade: -1 } },
  { $limit: 1 }
])
```

**Output:** 'Algorithms and Data Structures' with avg GPA ~7.814

### 9. Find Class Dropped Most Times

**Command Typed:**

```javascript
db.students.aggregate([
  { $unwind: "$courses" },
  { $match: { "courses.course_status": "Dropped" } },
  { $group: { _id: "$courses.course_title", drops: { $sum: 1 } } },
  { $sort: { drops: -1 } },
  { $limit: 1 }
])
```

**Output:** 'Algorithms and Data Structures' dropped 244 times

### 10. Completed Classes by Class Type

**Command Typed:**

```javascript
db.students.aggregate([
  { $unwind: "$courses" },
  { $match: { "courses.course_status": "Complete" } },
  { $group: { _id: { $substrBytes: ["$courses.course_code", 0, 1] }, count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

**Output:** P: 6756, M: 4483, S: 4376, D: 3287, V: 2274, B: 1111

### 11. Add Field 'Hobbyist'

**Command Typed:**

```javascript
db.students.aggregate([
  {
    $addFields: {
      hobbyist: {
        $gt: [{ $size: "$hobbies" }, 3]
      }
    }
  },
  { $project: { first_name: 1, hobbies: 1, hobbyist: 1 } }
])
```

**Output:** Students flagged with `hobbyist: true` or `false`

### 12. Add Field 'Completed Classes'

**Command Typed:**

```javascript
db.students.aggregate([
  {
    $addFields: {
      completed_classes: {
        $size: {
          $filter: {
            input: "$courses",
            as: "course",
            cond: { $eq: ["$$course.course_status", "Complete"] }
          }
        }
      }
    }
  },
  { $project: { first_name: 1, completed_classes: 1 } }
])
```

**Output:** Field `completed_classes` showing number of completed courses

### 13. Final Document Transformation

**Command Typed:**

```javascript
db.students.aggregate([
  {
    $addFields: {
      GPA: {
        $avg: {
          $map: {
            input: {
              $filter: {
                input: "$courses",
                as: "course",
                cond: { $eq: ["$$course.course_status", "Complete"] }
              }
            },
            as: "completedCourse",
            in: "$$completedCourse.grade"
          }
        }
      },
      classesInProgress: {
        $size: {
          $filter: {
            input: "$courses",
            as: "course",
            cond: { $eq: ["$$course.course_status", "In Progress"] }
          }
        }
      },
      droppedClasses: {
        $size: {
          $filter: {
            input: "$courses",
            as: "course",
            cond: { $eq: ["$$course.course_status", "Dropped"] }
          }
        }
      }
    }
  },
  { $project: { first_name: 1, GPA: 1, classesInProgress: 1, droppedClasses: 1 } }
])
```

**Output:**
Example:

```json
{
  "_id": ObjectId(...),
  "first_name": "Nikos",
  "GPA": 8,
  "classesInProgress": 1,
  "droppedClasses": 0
}
```

---

## Conclusion

All project tasks outlined in `Proj2_MongoDB.pdf` have been successfully completed. The dataset was loaded, queried, grouped, transformed, and cleaned according to specifications. This project involved practical experience with the aggregation pipeline, filtering, grouping, mapping, and transforming MongoDB documents efficiently.

---

## Notes

- Some students have `GPA: null` because they have no completed classes.
- Queries were run inside MongoDB Shell (mongosh 2.5.0).
- Database used: `studentsDB`, collection used: `students`.