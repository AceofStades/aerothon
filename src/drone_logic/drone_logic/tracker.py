import cv2
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Image
from ultralytics import YOLO


class AutonomousTracker(Node):
    def __init__(self):
        super().__init__("autonomous_tracker")

        self.subscription = self.create_subscription(
            Image, "/camera/image_raw", self.image_callback, 10
        )
        self.vel_publisher = self.create_publisher(
            Twist, "/mavros/setpoint_velocity/cmd_vel_unstamped", 10
        )

        self.bridge = CvBridge()
        self.model = YOLO("yolov8n.pt")

        # Split our tuning parameters so we can adjust them independently
        self.Kp_pitch = 0.005  # Forward/Back speed
        self.Kp_yaw = 0.005  # Turning speed

        self.get_logger().info("🎯 Target Lock V2 Online. Filter: Persons & Cars only.")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            height, width, _ = cv_image.shape
            center_x, center_y = int(width / 2), int(height / 2)

            # --- THE PROP BLINDERS (ROI MASKING) ---
            # Paint the top-left corner black (from x=0 to 20% width, y=0 to 30% height)
            cv2.rectangle(
                cv_image, (0, 0), (int(width * 0.2), int(height * 0.3)), (0, 0, 0), -1
            )
            # Paint the top-right corner black
            cv2.rectangle(
                cv_image,
                (int(width * 0.8), 0),
                (width, int(height * 0.3)),
                (0, 0, 0),
                -1,
            )

            # Now YOLO only looks at the unmasked center region!
            results = self.model(cv_image, classes=[0, 2], verbose=False)

            twist = Twist()
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            twist.linear.z = 0.0
            twist.angular.z = 0.0  # Initialize Yaw

            if len(results[0].boxes) > 0:
                box = results[0].boxes[0].xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = map(int, box)

                obj_cx = int((x1 + x2) / 2)
                obj_cy = int((y1 + y2) / 2)

                cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(cv_image, (obj_cx, obj_cy), 5, (0, 0, 255), -1)
                cv2.line(
                    cv_image, (center_x, center_y), (obj_cx, obj_cy), (255, 0, 0), 2
                )

                err_x = obj_cx - center_x
                err_y = obj_cy - center_y

                # THE LOGIC UPDATE:
                # Vertical error controls Pitch (Forward/Back)
                twist.linear.x = -float(err_y) * self.Kp_pitch

                # Horizontal error controls Yaw (Turning left/right)
                # Note: MAVROS might need a positive or negative sign here depending on the drone's IMU orientation.
                # If it turns away from the target, flip this to positive float(err_x)!
                twist.angular.z = -float(err_x) * self.Kp_yaw

                # Roll is kept at zero unless we decide to build an Orbit function later
                twist.linear.y = 0.0

                self.get_logger().info(
                    f"Locked: Pitch {twist.linear.x:.2f} | Yaw {twist.angular.z:.2f}"
                )

            self.vel_publisher.publish(twist)

            cv2.circle(cv_image, (center_x, center_y), 5, (0, 255, 255), -1)
            cv2.imshow("AEROTHON Tracking HUD", cv_image)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Matrix glitch: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = AutonomousTracker()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
