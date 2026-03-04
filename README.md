# 🏎️ Clothoid-R Autonomous Driving Simulator
본 프로젝트는 자율주행 알고리즘(Pure Pursuit, MPC, Stanley 등) 및 센서 퓨전 테스트를 위한 ROS 2 - Gazebo 기반의 차량 시뮬레이션 환경입니다.

## 🖥️ 운영 환경 (Operating Environment)
* **OS:** Ubuntu 24.04 LTS (또는 22.04 LTS)
* **ROS 2:** [Kilted]
* **Simulator:** Gazebo Sim (Ionic)
* **Dependencies:** `ros_gz_bridge`, `xacro`

## ⚙️ 사전 준비 및 빌드 (Installation & Build)
ROS 2 워크스페이스를 생성하고 패키지를 빌드합니다.

### 1. Git clone
```bash
git clone https://github.com/ttaehyun/Autonomous-Racing-Simulator.git
```

```bash
# 1. 워크스페이스 생성 및 클론
mkdir -p ~/simulate_ws/src
cd ~/simulate_ws/src
git clone [본인의 GitHub 레포지토리 주소]

# 2. 의존성 패키지 설치
sudo apt update
sudo apt install ros-[본인ROS버전]-ros-gz-bridge ros-[본인ROS버전]-xacro

# 3. 패키지 빌드
cd ~/simulate_ws
colcon build --packages-select server****
