import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from ultralytics import YOLO


class DroneVision(Node):
    def __init__(self):
        super().__init__("drone_vision")

        # 1. Subscribe to the drone's camera feed
        self.subscription = self.create_subscription(
            Image, "/camera/image_raw", self.image_callback, 10
        )

        self.bridge = CvBridge()

        # 2. Load the lightweight YOLOv8 AI model
        self.get_logger().info("🧠 Loading YOLOv8 AI Model...")
        self.model = YOLO("yolov8n.pt")
        self.get_logger().info("👁️ Drone Vision Online. Waiting for frames...")

    def image_callback(self, msg):
        try:
            # Convert ROS 2 Image -> OpenCV Image
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Run Object Detection
            results = self.model(cv_image, verbose=False)

            # Draw the glowing boxes around detected objects
            annotated_frame = results[0].plot()

            # Pop open a window to show us what the drone sees!
            cv2.imshow("AEROTHON AI Vision", annotated_frame)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Matrix glitch: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = DroneVision()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
