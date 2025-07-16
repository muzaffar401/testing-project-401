"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";

interface WorkoutSelectorProps {
    onWorkoutSelect: (workoutType: string) => void;
    selectedWorkout?: string;
}

// Define workout categories
const WORKOUT_CATEGORIES = {
    cardio: {
        title: "Cardio Training",
        workouts: [
            { id: "running", name: "Running", duration: "30 min", intensity: "Medium" },
            { id: "cycling", name: "Cycling", duration: "45 min", intensity: "Medium" },
            { id: "swimming", name: "Swimming", duration: "30 min", intensity: "Low" },
            { id: "hiit", name: "HIIT", duration: "20 min", intensity: "High" }
        ]
    },
    strength: {
        title: "Strength Training",
        workouts: [
            { id: "upper_body", name: "Upper Body", duration: "45 min", intensity: "Medium" },
            { id: "lower_body", name: "Lower Body", duration: "45 min", intensity: "Medium" },
            { id: "full_body", name: "Full Body", duration: "60 min", intensity: "High" },
            { id: "core", name: "Core Focus", duration: "30 min", intensity: "Medium" }
        ]
    },
    flexibility: {
        title: "Flexibility & Recovery",
        workouts: [
            { id: "yoga", name: "Yoga", duration: "45 min", intensity: "Low" },
            { id: "stretching", name: "Stretching", duration: "20 min", intensity: "Low" },
            { id: "pilates", name: "Pilates", duration: "45 min", intensity: "Medium" },
            { id: "mobility", name: "Mobility", duration: "30 min", intensity: "Low" }
        ]
    }
};

export function WorkoutSelector({ onWorkoutSelect, selectedWorkout }: WorkoutSelectorProps) {
    const getWorkoutColor = (workoutId: string) => {
        if (selectedWorkout === workoutId) {
            return 'bg-green-600 text-white hover:bg-green-700';
        }
        return 'bg-green-100 hover:bg-green-200 text-green-800 border-green-300';
    };

    const renderWorkoutCategory = (categoryKey: string, category: typeof WORKOUT_CATEGORIES.cardio) => (
        <div key={categoryKey} className="mb-6">
            <h4 className="text-sm font-semibold mb-3 text-center text-gray-700">{category.title}</h4>
            <div className="grid grid-cols-2 gap-2">
                {category.workouts.map(workout => (
                    <button
                        key={workout.id}
                        className={`p-3 rounded-lg border transition-colors ${getWorkoutColor(workout.id)}`}
                        onClick={() => onWorkoutSelect(workout.id)}
                    >
                        <div className="text-sm font-medium">{workout.name}</div>
                        <div className="text-xs opacity-80">{workout.duration}</div>
                        <div className="text-xs opacity-60">{workout.intensity}</div>
                    </button>
                ))}
            </div>
        </div>
    );

    return (
        <Card className="w-full max-w-md mx-auto my-4 bg-green-50">
            <CardContent className="p-4">
                <div className="text-center mb-4">
                    <h3 className="font-semibold text-lg mb-2 text-green-800">Select Your Workout</h3>
                    <p className="text-sm text-gray-600">Choose a workout type that fits your goals and schedule</p>
                </div>

                <div className="space-y-4">
                    {Object.entries(WORKOUT_CATEGORIES).map(([key, category]) => 
                        renderWorkoutCategory(key, category)
                    )}
                </div>

                {selectedWorkout && (
                    <div className="mt-4 p-3 bg-green-100 rounded-lg text-center">
                        <p className="text-sm font-medium text-green-800">
                            Selected: {selectedWorkout.replace('_', ' ').toUpperCase()}
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
} 