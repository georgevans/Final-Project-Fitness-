package com.example

import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.server.testing.*
import kotlin.test.Test
import kotlin.test.*
import kotlin.test.assertEquals
import io.ktor.client.statement.*

class RoutingTest {

    @Test
    fun testHomePageReturns200() = testApplication {
        application { configureRouting() }
        val response = client.get("/")
        assertEquals(HttpStatusCode.OK, response.status)
    }

    @Test
    fun testHomePageContainsFitnessTrackerHeading() = testApplication {
        application { configureRouting() }
        val response = client.get("/")
        val body = response.bodyAsText()
        assertTrue(body.contains("Fitness Tracker"))
    }

    @Test
    fun testHomePageContainsAddWorkoutLink() = testApplication {
        application { configureRouting() }
        val response = client.get("/")
        val body = response.bodyAsText()
        assertTrue(body.contains("/add-workout"))
    }

    @Test
    fun testHomePageContainsSettingsLink() = testApplication {
        application { configureRouting() }
        val response = client.get("/")
        val body = response.bodyAsText()
        assertTrue(body.contains("/settings"))
    }

    @Test
    fun testAddWorkoutReturns200() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout")
        assertEquals(HttpStatusCode.OK, response.status)
    }

    @Test
    fun testAddWorkoutContainsHeading() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout")
        val body = response.bodyAsText()
        assertTrue(body.contains("Add Workout"))
    }

    @Test
    fun testAddWorkoutContainsNameInput() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout")
        val body = response.bodyAsText()
        assertTrue(body.contains("workoutName"))
    }

    @Test
    fun testAddWorkoutContainsAddExerciseLink() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout")
        val body = response.bodyAsText()
        assertTrue(body.contains("add-exercise"))
    }

    @Test
    fun testAddExerciseReturns200() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/1/add-exercise/1")
        assertEquals(HttpStatusCode.OK, response.status)
    }

    @Test
    fun testAddExerciseContainsHeading() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/1/add-exercise/1")
        val body = response.bodyAsText()
        assertTrue(body.contains("Add Exercise"))
    }

    @Test
    fun testAddExerciseContainsExerciseNameInput() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/1/add-exercise/1")
        val body = response.bodyAsText()
        assertTrue(body.contains("exerciseName"))
    }

    @Test
    fun testAddExerciseContainsCardioOption() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/1/add-exercise/1")
        val body = response.bodyAsText()
        assertTrue(body.contains("cardio"))
    }

    @Test
    fun testAddExerciseContainsWeightsOption() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/1/add-exercise/1")
        val body = response.bodyAsText()
        assertTrue(body.contains("weights"))
    }

    @Test
    fun testAddExerciseContainsCardioFields() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/1/add-exercise/1")
        val body = response.bodyAsText()
        assertTrue(body.contains("duration"))
        assertTrue(body.contains("cals"))
        assertTrue(body.contains("distance"))
    }

    @Test
    fun testAddExerciseContainsWeightsFields() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/1/add-exercise/1")
        val body = response.bodyAsText()
        assertTrue(body.contains("sets"))
        assertTrue(body.contains("reps"))
        assertTrue(body.contains("difficulty"))
    }

    @Test
    fun testAddExerciseWithNonNumericIdsIsFine() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/abc/add-exercise/xyz")
        assertEquals(HttpStatusCode.OK, response.status)
    }

    @Test
    fun testAddExerciseContainsSaveButtons() = testApplication {
        application { configureRouting() }
        val response = client.get("/add-workout/1/add-exercise/1")
        val body = response.bodyAsText()
        assertTrue(body.contains("Save Cardio Exercise"))
        assertTrue(body.contains("Save Weights Exercise"))
    }
    

    @Test
    fun testWeightExerciseStoresCorrect() {
        val exercise = WeightExercise(
            exerciseName = "Bench Press",
            exerciseId = 1,
            sets = listOf(
                SetEntry(reps = 10, weight = 60, difficulty = 7),
                SetEntry(reps = 8, weight = 65, difficulty = 8)
            )
        )
        assertEquals(2, exercise.sets.size)
        assertEquals(10, exercise.sets[0].reps)
        assertEquals(65, exercise.sets[1].weight)
    }

    @Test
    fun testCardioExerciseStoresCorrect() {
        val exercise = CardioExercise(
            exerciseName = "Run",
            exerciseId = 1,
            entries = listOf(CardioEntry(duration = 30, cals = 300, distance = 5))
        )
        assertEquals(1, exercise.entries.size)
        assertEquals(300, exercise.entries[0].cals)
    }
}