cmake_minimum_required(VERSION 3.8)
project(turtle_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(turtlesim REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# 실행 파일 정의
add_executable(distance_publisher src/distance_publisher.cpp)
add_executable(distance_subscriber src/distance_subscriber.cpp)

# 의존 라이브러리 연결
ament_target_dependencies(distance_publisher rclcpp std_msgs turtlesim)
ament_target_dependencies(distance_subscriber rclcpp std_msgs)

# install/ 로 설치 (ros2 run이 찾을 수 있게)
install(TARGETS
  distance_publisher
  distance_subscriber
  DESTINATION lib/${PROJECT_NAME})

ament_package()
