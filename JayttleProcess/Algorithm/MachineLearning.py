import numpy as np
from typing import Tuple


class LinearClassifier:
    def __init__(self, num_features: int) -> None:
        # 初始化权重和偏置
        self.weights: np.ndarray = np.zeros(num_features)
        self.bias: float = 0.0

    def predict(self, X: np.ndarray) -> np.ndarray:
        # 计算预测值
        return np.dot(X, self.weights) + self.bias

    def train(self, X: np.ndarray, y: np.ndarray, learning_rate: float = 0.1, num_epochs: int = 100) -> None:
        # 使用梯度下降法训练模型
        for epoch in range(num_epochs):
            for i in range(len(X)):
                # 计算预测值
                y_pred = self.predict(X[i])
                # 计算误差
                error = y[i] - y_pred
                # 更新权重和偏置
                self.weights += learning_rate * error * X[i]
                self.bias += learning_rate * error

class MulticlassSVM:
    def __init__(self, num_classes: int, num_features: int, learning_rate: float = 0.01, lambda_param: float = 0.01) -> None:
        self.num_classes: int = num_classes
        self.num_features: int = num_features
        self.learning_rate: float = learning_rate
        self.lambda_param: float = lambda_param
        self.weights: np.ndarray = np.random.randn(num_classes, num_features)
        self.bias: np.ndarray = np.zeros(num_classes)

    def hinge_loss(self, scores: np.ndarray, correct_class_index: int) -> float:
        margins: np.ndarray = np.maximum(0, scores - scores[correct_class_index] + 1)
        margins[correct_class_index] = 0
        return np.sum(margins)

    def compute_loss(self, X: np.ndarray, y: np.ndarray) -> float:
        num_samples: int = X.shape[0]
        scores: np.ndarray = np.dot(X, self.weights.T) + self.bias
        correct_class_scores: np.ndarray = scores[np.arange(num_samples), y]
        loss: float = np.mean([self.hinge_loss(scores[i], y[i]) for i in range(num_samples)])
        loss += 0.5 * self.lambda_param * np.sum(self.weights ** 2)  # 添加 L2 正则化项
        return loss

    def compute_gradients(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        num_samples: int = X.shape[0]
        scores: np.ndarray = np.dot(X, self.weights.T) + self.bias
        correct_class_indices: Tuple[np.ndarray, np.ndarray] = (np.arange(num_samples), y)
        margins: np.ndarray = np.maximum(0, scores - scores[correct_class_indices[0], correct_class_indices[1]][:, None] + 1)
        margins[correct_class_indices] = 0
        binary_grads: np.ndarray = (margins > 0).astype(float)
        binary_grads[correct_class_indices] = -np.sum(binary_grads, axis=1)
        dW: np.ndarray = np.dot(binary_grads.T, X) / num_samples + self.lambda_param * self.weights
        db: np.ndarray = np.mean(binary_grads, axis=0)
        return dW, db

    def train(self, X: np.ndarray, y: np.ndarray, num_epochs: int = 100) -> None:
        for epoch in range(num_epochs):
            dW, db = self.compute_gradients(X, y)
            self.weights -= self.learning_rate * dW
            self.bias -= self.learning_rate * db
            loss = self.compute_loss(X, y)
            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        scores: np.ndarray = np.dot(X, self.weights.T) + self.bias
        return np.argmax(scores, axis=1)