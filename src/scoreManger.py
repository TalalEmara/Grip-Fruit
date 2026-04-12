class ScoreManager:
    def __init__(self):

        self.total_score = 0
        self.streak = 0

        self.POINTS_PERFECT = 10
        self.POINTS_COMPENSATED = 5
        self.POINTS_PENALTY = -5

        self.stats = {
            "perfect_grips": 0,
            "compensated_grips": 0,
            "wrong_objects": 0,
            "total_attempts": 0
        }

    def process_grip(self, is_correct_target: bool, compensation_detected: bool) -> dict:
        """
        Evaluates a grip event, updates the score, logs clinical stats,
        and returns the results of the current action.
        """
        self.stats["total_attempts"] += 1
        points_awarded = 0
        feedback_event = ""

        # Condition 1: Squeezed the wrong object
        if not is_correct_target:
            points_awarded = self.POINTS_PENALTY
            self.stats["wrong_objects"] += 1
            self.streak = 0
            feedback_event = "penalty_wrong_object"

        # Condition 2: Squeezed right object, but with compensatory movement
        elif compensation_detected:
            points_awarded = self.POINTS_COMPENSATED
            self.stats["compensated_grips"] += 1
            self.streak = 0  # Reset streak because form was broken
            feedback_event = "score_compensated"

        # Condition 3: Perfect execution
        else:
            points_awarded = self.POINTS_PERFECT
            self.stats["perfect_grips"] += 1
            self.streak += 1
            feedback_event = "score_perfect"

            # Optional: Add a bonus for stringing together good reps without compensation
            if self.streak >= 3:
                points_awarded += 2
                feedback_event = "score_perfect_streak"

        # Update total score
        self.total_score += points_awarded

        # Optional: Prevent score from dropping below 0 to avoid discouraging the patient
        if self.total_score < 0:
            self.total_score = 0

        # Return a dictionary so the game engine (UI/Audio) knows what just happened
        return {
            "points_awarded": points_awarded,
            "current_total": self.total_score,
            "event_type": feedback_event,
            "current_streak": self.streak
        }

    def get_clinical_summary(self) -> dict:
        """
        Returns a summary of the session data.
        Save this to a database or JSON file for the therapist to review.
        """
        return {
            "final_score": self.total_score,
            "statistics": self.stats
        }

    def reset_session(self):
        """Resets the manager for a new game or new patient."""
        self.__init__()