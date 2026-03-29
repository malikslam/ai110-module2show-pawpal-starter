```mermaid
classDiagram
    class Owner {
        +String name
        +int available_minutes_per_day
        +String preferences
    }

    class Pet {
        +String name
        +String species
        +int age
        +String health_notes
        +Owner owner
        +List~Task~ tasks
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +String time_of_day_constraint
        +String frequency
        +bool is_required
    }

    class Scheduler {
        +Pet pet
        +String plan_weekday
        +generate_plan() DailyPlan
    }

    class DailyPlan {
        +List~ScheduledTask~ scheduled
        +List~Task~ skipped
        +explain() String
        +total_time() int
    }

    class ScheduledTask {
        +Task task
        +String start_time
        +String reason
    }

    Owner "1" --> "1" Pet : owns
    Pet "1" --> "1" Scheduler : used by
    Owner "1" --> "1" Scheduler : provides available_minutes
    Pet "1" --> "many" Task : has
    Scheduler --> DailyPlan : generates
    DailyPlan "1" --> "many" ScheduledTask : contains
    DailyPlan "1" --> "many" Task : skips
    ScheduledTask --> Task : wraps
```
