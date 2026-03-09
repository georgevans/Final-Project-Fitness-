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
                            id = "workoutName"
                            type = InputType.text
                            placeholder = "Workout Name"
                        }
                        // when clicked will need to gen id
                        a(href="/add-workout/1/add-exercise/1") { +"Add Exercise to workout" } // passed workout id and a exercise id to the  
                    }
                }
            }
        }

        get("/add-workout/{workoutId}/add-exercise/{exerciseId}") {
            val workoutId = call.parameters["workoutId"]?.toIntOrNull() ?: 1
            val exerciseId = call.parameters["exerciseId"]?.toIntOrNull() ?: 1
            
            call.respondHtml {
                body {
                    div {
                        h1 { +"Add Exercise" }

                        input {
                            id = "exerciseName"
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
                            input { id = "duration"; type = InputType.number; placeholder = "Duration"}
                            input { id = "cals"; type = InputType.number; placeholder = "Calories Burned" }
                            input { id = "distance"; type = InputType.number; placeholder = "Distance" }
                            button { 
                                onClick = "saveCardio($workoutId, $exerciseId)"
                                +"Save Cardio Exercise" }
                        }

                        div {
                            id = "weightsFields"
                            style = "display:none"
                            input { id = "sets"; type = InputType.number; placeholder = "Sets"}
                            input { id = "reps"; type = InputType.number; placeholder = "Reps per set" }
                            input { id = "weight"; type = InputType.number; placeholder = "Weight" }
                            input { id = "difficulty"; type = InputType.number; placeholder = "Difficulty (1-10)" }
                            button { 
                                onClick = "saveWeights($workoutId, $exerciseId)"
                                +"Save Weights Exercise" }
                        }

                        script { // shows relevant forms when type changed.
                            unsafe {
                                +"""
                                function getInputVal(id) {
                                    const element = document.getElementById(id);
                                    if (!element) { alert(id + ' not found'); return null; }
                                    const value = element.value.trim();
                                    if (!value || value === '') {
                                        alert(id + ' cannot be empty');
                                    }
                                    return value;
                                }

                                function safeInt(value, fieldName) { 
                                    const parsed = parseInt(val2);
                                    if (isNaN(parsed)) { alert(fieldName + ' must be a whole number'); return null; }
                                    return parsed;
                                }

                                function safeFloat(value, fieldName) {
                                    const parsed = parseFloat(value); 
                                    if (isNaN(parsed)) { alert(fieldName + ' must be a number'); return null; }
                                    return parsed;
                                }

                                function toggleFields(type) {
                                    document.getElementById('cardioFields').style.display = type === 'cardio' ? 'block' : 'none';
                                    document.getElementById('weightsFields').style.display = type === 'weights' ? 'block' : 'none';
                                };

                                function saveCardio(workoutId, exerciseId) {
                                    const type = document.getElementById('exerciseType').value;
                                    if (!type || type === '') { alert('Exercise type must be selected'); return; }

                                    const exerciseName = getInputVal('exerciseName');
                                    const duration = getInputVal('duration');
                                    const cals = getInputVal('cals');
                                    const distance = getInputVal('distance');
                                    
                                    if (!exerciseName || !duration || !cals || !distance) return;

                                    if (duration <= 0) { alert('Duration must be greater than 0'); return; }
                                    if (cals < 0) { alert('Calories cannot be negative'); return; }
                                    if (distance <= 0) { alert('Distance must be greater than 0'); return; }
                                    
                                    const data = {
                                        workoutId: workoutId,
                                        exerciseId: exerciseId,
                                        exerciseName: exerciseName,
                                        duration: duration,
                                        cals: cals,
                                        distance: distance
                                    };
                                    console.log(data);
                                    // then send to backend with POST
                                    window.location.href = '/add-workout';
                                }
                                function saveWeights(workoutId, exerciseId) {
                                    const type = document.getElementById('exerciseType').value;
                                    if (!type || type === '') { alert('Exercise type must be selected'); return; }
                                    
                                    const exerciseName = getInputVal('exerciseName');
                                    const setsRaw = getInputVal('sets');
                                    const repsRaw = getInputVal('reps');
                                    const weightRaw = getInputVal('weight');
                                    const difficultyRaw = getInputVal('difficulty');
                                    
                                    if (!exerciseName || !setsRaw || !repsRaw || !weightRaw || !difficultyRaw) return;
                                    
                                    const sets = safeInt(setsRaw, 'Sets');
                                    const reps = safeInt(repsRaw, 'Reps');
                                    const weight = safeFloat(weightRaw, 'Weight');
                                    const difficulty = safeInt(difficultyRaw, 'Difficulty');
                                    
                                    if (sets === null || reps === null || weight === null || difficulty === null) return;
                                    
                                    if (sets <= 0) { alert('Sets must be greater than 0'); return; }
                                    if (reps <= 0) { alert('Reps must be greater than 0'); return; }
                                    if (weight <= 0) { alert('Weight must be greater than 0'); return; }
                                    if (difficulty < 1 || difficulty > 10) { alert('Difficulty must be between 1 and 10'); return; }
                                    

                                    const data = {
                                        workoutId: workoutId,
                                        exerciseId: exerciseId,
                                        exerciseName: exerciseName,
                                        sets: parseInt(sets),
                                        reps: parseInt(reps),
                                        weight: parseFloat(weight),
                                        difficulty: difficultyVal
                                    };
                                    console.log(data);
                                    // send to backend with POST
                                    window.location.href = '/add-workout'
                                }
                                """.trimIndent()
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
// Null protections for inputs
// Workout name currently doesnt save
// Input validation for forms
// Save form inputs into object for sending to server (to insert into db)
