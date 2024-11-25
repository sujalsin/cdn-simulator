import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)

class TrafficPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.accuracy = 0.0
        self.is_trained = False
        
        # Generate some initial training data
        self.generate_initial_data()
        
    def generate_initial_data(self):
        """Generate synthetic training data for initial model training."""
        # Generate 1000 samples of synthetic data
        n_samples = 1000
        
        # Time features (hour of day, day of week)
        hours = np.random.randint(0, 24, n_samples)
        days = np.random.randint(0, 7, n_samples)
        
        # Location features (random distribution across nodes)
        locations = np.random.randint(0, 5, n_samples)  # Assuming 5 nodes
        
        # Content type features (e.g., video, image, text)
        content_types = np.random.randint(0, 3, n_samples)
        
        # Generate target variable (traffic volume) based on features
        traffic = (
            10 * np.sin(hours * np.pi / 12)  # Daily pattern
            + 5 * np.sin(days * np.pi / 3.5)  # Weekly pattern
            + 2 * locations  # Location impact
            + 3 * content_types  # Content type impact
            + np.random.normal(0, 1, n_samples)  # Random noise
        )
        traffic = np.maximum(traffic, 0)  # Ensure non-negative values
        
        # Combine features
        self.initial_data = {
            'features': np.column_stack([hours, days, locations, content_types]),
            'target': traffic
        }
        
        # Train the model with initial data
        self.train(self.initial_data)
        
    def prepare_features(self, data):
        """Prepare features for training or prediction."""
        if isinstance(data, dict) and 'features' in data:
            return data['features'], data['target']
        
        # If data is a list of dictionaries, convert to numpy arrays
        features = []
        targets = []
        for record in data:
            features.append([
                record.get('hour', 0),
                record.get('day', 0),
                record.get('location', 0),
                record.get('content_type', 0)
            ])
            targets.append(record.get('traffic', 0))
        
        return np.array(features), np.array(targets)

    def train(self, data):
        """Train the model with historical traffic data."""
        try:
            X, y = self.prepare_features(data)
            
            # Split data for training and validation
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train the model
            self.model.fit(X_train, y_train)
            
            # Calculate accuracy (using R² score)
            self.accuracy = self.model.score(X_val, y_val)
            self.is_trained = True
            
            logger.info(f"Model trained successfully. Accuracy (R² score): {self.accuracy:.4f}")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            self.is_trained = False
            self.accuracy = 0.0

    def predict(self, features):
        """Predict traffic volume for given features."""
        if not self.is_trained:
            logger.warning("Model not trained yet")
            return None
            
        try:
            X = np.array(features).reshape(1, -1)
            return self.model.predict(X)[0]
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return None

    def get_accuracy(self):
        """Return the current model accuracy."""
        return self.accuracy if self.is_trained else 0.0
