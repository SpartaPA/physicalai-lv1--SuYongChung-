#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float32.hpp>
#include <turtlesim/msg/pose.hpp>
#include <cmath>

class DistancePublisher : public rclcpp::Node
{
public:
    DistancePublisher() : Node("distance_publisher_cpp")
    {
        pose_sub_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose", 10,
            [this](const turtlesim::msg::Pose::SharedPtr msg) {
                last_pose_ = *msg;
                pose_received_ = true;
            });

        dist_pub_ = this->create_publisher<std_msgs::msg::Float32>(
            "/turtle_distance", 10);

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&DistancePublisher::timer_callback, this));

        RCLCPP_INFO(this->get_logger(), "C++ Distance publisher started at 10 Hz");
    }

private:
    void timer_callback()
    {
        if (!pose_received_) return;

        auto msg = std_msgs::msg::Float32();
        msg.data = std::sqrt(
            last_pose_.x * last_pose_.x + last_pose_.y * last_pose_.y);
        dist_pub_->publish(msg);
    }

    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_sub_;
    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr dist_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    turtlesim::msg::Pose last_pose_;
    bool pose_received_ = false;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DistancePublisher>());
    rclcpp::shutdown();
    return 0;
}
