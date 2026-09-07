#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float32.hpp>

class DistanceSubscriber : public rclcpp::Node
{
public:
    DistanceSubscriber() : Node("distance_subscriber_cpp")
    {
        dist_sub_ = this->create_subscription<std_msgs::msg::Float32>(
            "/turtle_distance", 10,
            std::bind(&DistanceSubscriber::dist_callback, this,
                      std::placeholders::_1));

        RCLCPP_INFO(this->get_logger(), "C++ Distance subscriber started");
    }

private:
    void dist_callback(const std_msgs::msg::Float32::SharedPtr msg)
    {
        RCLCPP_INFO(this->get_logger(), "distance=%.2f", msg->data);
    }

    rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr dist_sub_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DistanceSubscriber>());
    rclcpp::shutdown();
    return 0;
}
