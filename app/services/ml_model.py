"""
SafeLoop Calibrated Scikit-Learn Risk Model (L3: Decide)
Owned by: Person 4 (Arun)

Transforms text, entity meta-features, and baseline anomaly signals into a calibrated
probability distribution: P(scam | features) in [0.0, 1.0].

Architecture:
1. Feature Extractor:
   - TF-IDF Word & Character N-Grams (handles Indian scam vocabulary, typos, and urgency)
   - Weighted Dense Meta-Features:
     * has_upi, has_phone, has_link, is_suspicious_tld
     * log_amount
     * keyword_density (digital arrest, electricity, lottery, distress)
     * baseline_anomaly_score
2. Classifier:
   - Calibrated Logistic Regression with balanced class weighting
   - Outputs calibrated risk probabilities rather than raw heuristics
"""

import os
import math
from typing import Dict, Any, List, Optional, Tuple

try:
    import joblib
    import numpy as np
    from scipy.sparse import hstack, csr_matrix
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
except ImportError:
    joblib = None
    np = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "risk_classifier.joblib")


class SafeLoopRiskClassifier:
    """End-to-end ML model for fraud risk probability estimation."""

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.model = None
        self.feature_names: List[str] = []
        self.is_trained: bool = False

    def _extract_meta_features(
        self,
        text: str,
        entities: Dict[str, Any],
        baseline_score: float = 0.0
    ) -> List[float]:
        """Extracts dense domain-specific signals from text and extracted entities."""
        text_lower = (text or "").lower()
        
        # Safe numeric parsing of amount (prevent math domain errors on negative or invalid numbers)
        amount_val = 0.0
        amounts = entities.get("amounts", [])
        if amounts:
            try:
                first_amt = float(amounts[0])
                amount_val = max(first_amt, 0.0)
            except (ValueError, TypeError):
                amount_val = 0.0
        log_amount = math.log10(amount_val + 1.0) / 6.0  # Normalized (up to ₹10 Lakh)

        has_upi = 1.0 if entities.get("upi_ids") else 0.0
        has_phone = 1.0 if entities.get("phones") else 0.0
        has_link = 1.0 if entities.get("links") else 0.0

        # High-risk TLD indicator
        links = entities.get("links", [])
        has_suspicious_tld = 1.0 if any(
            any(tld in l.lower() for tld in [".info", ".cc", ".top", ".xyz", ".club"])
            for l in links
        ) else 0.0

        # Psychological trigger density
        urgency_terms = ["immediately", "within", "urgent", "tonight", "hours", "minutes", "disconnect", "blocked", "urgently"]
        urgency_count = sum(1.0 for term in urgency_terms if term in text_lower)
        urgency_score = min(urgency_count / 2.0, 1.0)

        # Coercion / Authority terms
        authority_terms = ["police", "cbi", "warrant", "arrest", "court", "trai", "customs", "cyber", "laundering", "inspector"]
        authority_count = sum(1.0 for term in authority_terms if term in text_lower)
        authority_score = min(authority_count / 2.0, 1.0)

        # Financial lure terms
        lure_terms = ["lottery", "won", "prize", "refund", "pre-approved", "earn", "daily", "activation", "kbc", "draw"]
        lure_count = sum(1.0 for term in lure_terms if term in text_lower)
        lure_score = min(lure_count / 2.0, 1.0)

        raw_meta = [
            has_upi,
            has_phone,
            has_link,
            has_suspicious_tld,
            log_amount,
            urgency_score,
            authority_score,
            lure_score,
            min(max(baseline_score, 0.0), 1.0)
        ]

        # Scale meta-features by 3.0 to match the TF-IDF feature space density
        return [v * 3.0 for v in raw_meta]

    def fit(self, samples: List[Dict[str, Any]], max_features: int = 500) -> "SafeLoopRiskClassifier":
        """Trains the TF-IDF vectorizer and calibrated classifier on labelled samples."""
        if joblib is None or np is None:
            raise ImportError("scikit-learn and joblib must be installed to train the model.")

        texts = [s.get("text", "") for s in samples]
        y = np.array([1 if s.get("category") == "scam" else 0 for s in samples])

        # 1. Fit TF-IDF on word n-grams (1-2) with sublinear term frequency
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=max_features,
            sublinear_tf=True,
            strip_accents="unicode"
        )
        X_text = self.vectorizer.fit_transform(texts)

        # 2. Extract meta-features for all training rows
        meta_features_list = [
            self._extract_meta_features(
                s.get("text", ""),
                s.get("entities", {}),
                s.get("baseline_anomaly", 0.0)
            )
            for s in samples
        ]
        X_meta = csr_matrix(meta_features_list)

        # 3. Combine text n-grams and dense signals
        X_combined = hstack([X_text, X_meta]).tocsr()

        # 4. Train calibrated model
        base_lr = LogisticRegression(C=10.0, class_weight="balanced", max_iter=1000, random_state=42)
        base_lr.fit(X_combined, y)

        self.model = base_lr
        self.is_trained = True
        return self

    def predict_proba(
        self,
        text: str,
        entities: Optional[Dict[str, Any]] = None,
        baseline_score: float = 0.0
    ) -> float:
        """Returns calibrated probability P(scam | features) between 0.0 and 1.0."""
        if not self.is_trained or self.model is None or self.vectorizer is None:
            return 0.5

        entities = entities or {}
        X_text = self.vectorizer.transform([text or ""])
        meta_features = [self._extract_meta_features(text, entities, baseline_score)]
        X_meta = csr_matrix(meta_features)

        X_combined = hstack([X_text, X_meta]).tocsr()
        probs = self.model.predict_proba(X_combined)[0]
        return float(probs[1])

    def explain(
        self,
        text: str,
        entities: Optional[Dict[str, Any]] = None,
        top_k: int = 3
    ) -> List[str]:
        """Explains which linguistic or metadata features contributed most to the ML score."""
        if not self.is_trained or self.model is None or self.vectorizer is None:
            return []

        explanations = []
        text_lower = (text or "").lower()
        feature_names = list(self.vectorizer.get_feature_names_out())
        coefs = self.model.coef_[0][:len(feature_names)]

        # Find words present in text with highest positive weights
        word_scores = []
        for word, weight in zip(feature_names, coefs):
            if weight > 0.3 and word in text_lower:
                word_scores.append((word, weight))

        word_scores.sort(key=lambda x: x[1], reverse=True)
        for word, weight in word_scores[:top_k]:
            explanations.append(f"ML pattern match: High-weight scam indicator term '{word}'")

        return explanations

    def save(self, filepath: str = MODEL_PATH):
        """Serializes model artifacts to disk using joblib."""
        if joblib is None:
            return
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "vectorizer": self.vectorizer,
            "model": self.model,
            "is_trained": self.is_trained
        }, filepath)

    @classmethod
    def load(cls, filepath: str = MODEL_PATH) -> Optional["SafeLoopRiskClassifier"]:
        """Loads serialized model from disk, returning None if file does not exist."""
        if joblib is None or not os.path.exists(filepath):
            return None
        try:
            bundle = joblib.load(filepath)
            instance = cls()
            instance.vectorizer = bundle.get("vectorizer")
            instance.model = bundle.get("model")
            instance.is_trained = bundle.get("is_trained", False)
            return instance
        except Exception:
            return None


# Global singleton instance for high-throughput in-memory inference
_ml_classifier_instance: Optional[SafeLoopRiskClassifier] = None


def get_ml_classifier() -> Optional[SafeLoopRiskClassifier]:
    """Loads and caches the ML classifier in memory."""
    global _ml_classifier_instance
    if _ml_classifier_instance is None:
        _ml_classifier_instance = SafeLoopRiskClassifier.load()
    return _ml_classifier_instance
