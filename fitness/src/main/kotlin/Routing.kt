package com.example

import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.plugins.statuspages.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.sessions.*
import kotlinx.serialization.Serializable
import org.jetbrains.exposed.sql.*
import io.ktor.server.html.*
import kotlinx.html.*
import io.ktor.server.http.content.*

data class SetEntry(
    val reps: Int,
    val weight: Int,
    val difficulty: Int
)

data class WeightExercise(
    val exerciseName: String,
    val exerciseId: Int,
    val sets: List<SetEntry>
)

data class CardioEntry(
    val duration: Int,
    val cals: Int,
    val distance: Int
)

data class CardioExercise(
    val exerciseName: String,
    val exerciseId: Int,
    val entries: List<CardioEntry>
)

data class Workout(
    val userId: Int,
    val workoutId: Int,
    val name: String,
    val cardio: Boolean,
    val weights: Boolean,
    val weightExercises: List<WeightExercise>,
    val cardioExercises: List<CardioExercise>,
    val distanceUnit: String = "km",
    val timeUnit: String = "minutes",
    val weightUnit: String = "kg"
)

fun Application.configureRouting() {
    install(StatusPages) {
        exception<Throwable> { call, cause ->
            call.respondText(text = "500: $cause" , status = HttpStatusCode.InternalServerError)
        }
    }
    routing {
        staticResources("/static", "static") // sets static file path as resources folder (store css and imgs in here)

        get("/") { // first page
            call.respondHtml {
                head {
                    title { +"Home - Fitness Tracker"}
                }
                body {
                    div {
                        h1 { +"Fitness Tracker" }
                        a(href = "/settings") { +"Settings" } // redirects user to settings page
                    }
                    div {
                        img {
                            src = "/static/img.png" // temp image, will be actual bar graph once data recording possible
                            alt = "Image description"
                        }
                    }

                    div {
                        h3 { +"Metrics"} // will contain weekly/monthly summary of cals burned, distance ran etc
                    }

                    div {
                        a(href="/add-workout") { +"Add Workout"} // link to add workout form
                    }
                }
            }
        }

        get("/add-workout") { 
            // generate workout id up 
            call.respondHtml {
                head {
                    title { +"Add Workout"}
                }
                body {
                    div {
                        h1 { +"Add Workout" }
                        input {
                            type = InputType.text
                            placeholder = "Workout Name"
                        }
                        // when clicked will need to gen id
                        a(href="/add-workout/1/add-exercise/1") { +"Add Exercise to workout" } // passed workout id and a exercise id to the  
                    }
                }
            }
        }

        get("/add-workout/{workout_id}/add-exercise/{exercise_id}") {
            call.respondHtml {
                body {
                    div {
                        h1 { +"Add Exercise" }

                        input {
                            type = InputType.text
                            placeholder = "Exercise Name"
                        }

                        select {
                            id = "exerciseType"
                            onChange = "toggleFields(this.value)"
                            option { value = ""; +"Select Type" }
                            option {value = "cardio"; +"Cardio"}
                            option {value = "weights"; +"Weights"}
                        }

                        div {
                            id = "cardioFields"
                            style = "display:none"
                            input { type = InputType.number; placeholder = "Duration"}
                            input { type = InputType.number; placeholder = "Calories Burned" }
                            input { type = InputType.number; placeholder = "Distance" }
                            button { +"Save Cardio Exercise" }
                        }

                        div {
                            id = "weightsFields"
                            style = "display:none"
                            input { type = InputType.number; placeholder = "Sets"}
                            input { type = InputType.number; placeholder = "Reps per set" }
                            input { type = InputType.number; placeholder = "Weight" }
                            input { type = InputType.number; placeholder = "Difficulty (1-10)" }
                            button { +"Save Weights Exercise" }
                        }

                        script { // shows relevant forms when type changed.
                            unsafe {
                                +"function toggleFields(type) {"
                                +"  document.getElementById('cardioFields').style.display = type === 'cardio' ? 'block' : 'none';"
                                +"  document.getElementById('weightsFields').style.display = type === 'weights' ? 'block' : 'none';"
                                +"}"
                            }
                        }
                    }
                }
            }
        }
    }
}

// NEEDED before merge
// Testing
// Input validation for forms
// Save form inputs into object for sending to server (to insert into db)
