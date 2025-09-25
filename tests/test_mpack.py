#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock

# 添加脚本路径以便导入模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
scripts_path = os.path.join(project_root, 'common-services', 'NEBULA', '1.0.0', 'package', 'scripts')
alerts_path = os.path.join(scripts_path, 'alerts')

sys.path.insert(0, scripts_path)
sys.path.insert(0, alerts_path)

class TestNebulaUtils(unittest.TestCase):
    """测试Nebula工具函数"""
    
    def setUp(self):
        """测试前置设置"""
        # 模拟配置参数
        self.mock_params = Mock()
        self.mock_params.nebula_user = 'nebula'
        self.mock_params.nebula_group = 'nebula'
        self.mock_params.nebula_data_dir = '/var/lib/nebula'
        self.mock_params.nebula_log_dir = '/var/log/nebula'
        self.mock_params.nebula_pid_dir = '/var/run/nebula'
        self.mock_params.graphd_port = 9669
        self.mock_params.metad_port = 9559
        self.mock_params.storaged_port = 9779
    
    def test_is_port_open_success(self):
        """测试端口检查 - 成功情况"""
        try:
            from nebula_utils import is_port_open
            
            # 模拟成功的socket连接
            with patch('socket.socket') as mock_socket:
                mock_sock = Mock()
                mock_sock.connect_ex.return_value = 0
                mock_socket.return_value = mock_sock
                
                result = is_port_open(9669)
                self.assertTrue(result)
                mock_sock.connect_ex.assert_called_once()
                mock_sock.close.assert_called_once()
        except ImportError:
            self.skipTest("nebula_utils module not available")
    
    def test_is_port_open_failure(self):
        """测试端口检查 - 失败情况"""
        try:
            from nebula_utils import is_port_open
            
            # 模拟失败的socket连接
            with patch('socket.socket') as mock_socket:
                mock_sock = Mock()
                mock_sock.connect_ex.return_value = 1
                mock_socket.return_value = mock_sock
                
                result = is_port_open(9669)
                self.assertFalse(result)
        except ImportError:
            self.skipTest("nebula_utils module not available")

class TestAlertScripts(unittest.TestCase):
    """测试告警脚本"""
    
    def test_graphd_process_alert_success(self):
        """测试Graphd进程告警 - 成功情况"""
        try:
            import alert_graphd_process
            
            configurations = {
                '{{nebula-env/nebula_pid_dir}}/nebula-graphd.pid': '/tmp/test.pid',
                '{{nebula-graphd-site/port}}': '9669'
            }
            
            # 创建临时PID文件
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write('12345')
                pid_file = f.name
            
            configurations['{{nebula-env/nebula_pid_dir}}/nebula-graphd.pid'] = pid_file
            
            try:
                with patch('alert_graphd_process.is_process_running', return_value=True), \
                     patch('alert_graphd_process.is_port_accessible', return_value=True):
                    
                    result_code, labels = alert_graphd_process.execute(configurations)
                    self.assertEqual(result_code, 'OK')
                    self.assertIn('running and port 9669 is accessible', labels[0])
            finally:
                os.unlink(pid_file)
                
        except ImportError:
            self.skipTest("alert_graphd_process module not available")
    
    def test_graphd_process_alert_failure(self):
        """测试Graphd进程告警 - 失败情况"""
        try:
            import alert_graphd_process
            
            configurations = {
                '{{nebula-env/nebula_pid_dir}}/nebula-graphd.pid': '/tmp/nonexistent.pid',
                '{{nebula-graphd-site/port}}': '9669'
            }
            
            with patch('alert_graphd_process.is_process_running', return_value=False):
                result_code, labels = alert_graphd_process.execute(configurations)
                self.assertEqual(result_code, 'CRITICAL')
                self.assertIn('not running', labels[0])
                
        except ImportError:
            self.skipTest("alert_graphd_process module not available")

class TestConfigurationFiles(unittest.TestCase):
    """测试配置文件"""
    
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.common_services_dir = os.path.join(
            self.project_root, 'common-services', 'NEBULA', '1.0.0'
        )
    
    def test_mpack_json_valid(self):
        """测试mpack.json文件有效性"""
        mpack_file = os.path.join(self.project_root, 'mpack.json')
        
        self.assertTrue(os.path.exists(mpack_file), "mpack.json file should exist")
        
        with open(mpack_file, 'r') as f:
            try:
                mpack_data = json.load(f)
                self.assertIn('name', mpack_data)
                self.assertIn('version', mpack_data)
                self.assertIn('artifacts', mpack_data)
                self.assertEqual(mpack_data['name'], 'nebula-ambari-mpack')
            except json.JSONDecodeError as e:
                self.fail(f"mpack.json contains invalid JSON: {e}")
    
    def test_metainfo_xml_exists(self):
        """测试metainfo.xml文件存在"""
        metainfo_file = os.path.join(self.common_services_dir, 'metainfo.xml')
        self.assertTrue(os.path.exists(metainfo_file), "metainfo.xml should exist")
        
        # 检查文件内容包含关键元素
        with open(metainfo_file, 'r') as f:
            content = f.read()
            self.assertIn('NEBULA_GRAPHD', content)
            self.assertIn('NEBULA_METAD', content)
            self.assertIn('NEBULA_STORAGED', content)
    
    def test_metrics_json_valid(self):
        """测试metrics.json文件有效性"""
        metrics_file = os.path.join(self.common_services_dir, 'metrics.json')
        
        self.assertTrue(os.path.exists(metrics_file), "metrics.json should exist")
        
        with open(metrics_file, 'r') as f:
            try:
                metrics_data = json.load(f)
                self.assertIn('NEBULA', metrics_data)
                self.assertIn('Component', metrics_data['NEBULA'])
                self.assertIn('HostComponent', metrics_data['NEBULA'])
            except json.JSONDecodeError as e:
                self.fail(f"metrics.json contains invalid JSON: {e}")
    
    def test_alerts_json_valid(self):
        """测试alerts.json文件有效性"""
        alerts_file = os.path.join(self.common_services_dir, 'alerts.json')
        
        self.assertTrue(os.path.exists(alerts_file), "alerts.json should exist")
        
        with open(alerts_file, 'r') as f:
            try:
                alerts_data = json.load(f)
                self.assertIn('NEBULA', alerts_data)
                # 检查服务级别告警
                if 'service' in alerts_data['NEBULA']:
                    service_alerts = alerts_data['NEBULA']['service']
                    self.assertIsInstance(service_alerts, list)
                    # 检查是否有集群健康检查告警
                    cluster_health_alerts = [a for a in service_alerts if a.get('name') == 'nebula_cluster_health']
                    self.assertTrue(len(cluster_health_alerts) > 0, "Should have cluster health alert")
            except json.JSONDecodeError as e:
                self.fail(f"alerts.json contains invalid JSON: {e}")
    
    def test_configuration_files_exist(self):
        """测试配置文件存在"""
        config_dir = os.path.join(self.common_services_dir, 'configuration')
        
        required_configs = [
            'nebula-env.xml',
            'nebula-graphd-site.xml',
            'nebula-metad-site.xml',
            'nebula-storaged-site.xml',
            'nebula-log4j.xml'
        ]
        
        for config_file in required_configs:
            config_path = os.path.join(config_dir, config_file)
            self.assertTrue(os.path.exists(config_path), f"{config_file} should exist")

class TestScriptFiles(unittest.TestCase):
    """测试脚本文件"""
    
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.scripts_dir = os.path.join(
            self.project_root, 'common-services', 'NEBULA', '1.0.0', 'package', 'scripts'
        )
    
    def test_script_files_exist(self):
        """测试脚本文件存在"""
        required_scripts = [
            'params.py',
            'status_params.py',
            'nebula_utils.py',
            'graphd.py',
            'metad.py',
            'storaged.py',
            'console.py',
            'service_check.py'
        ]
        
        for script_file in required_scripts:
            script_path = os.path.join(self.scripts_dir, script_file)
            self.assertTrue(os.path.exists(script_path), f"{script_file} should exist")
    
    def test_alert_scripts_exist(self):
        """测试告警脚本文件存在"""
        alerts_dir = os.path.join(self.scripts_dir, 'alerts')
        
        required_alert_scripts = [
            'alert_graphd_process.py',
            'alert_metad_process.py',
            'alert_storaged_process.py',
            'alert_cluster_health.py',
            'alert_metad_leader.py'
        ]
        
        for script_file in required_alert_scripts:
            script_path = os.path.join(alerts_dir, script_file)
            self.assertTrue(os.path.exists(script_path), f"{script_file} should exist")

def run_tests():
    """运行所有测试"""
    print("Running Nebula Ambari Mpack Unit Tests...")
    print("=" * 50)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestNebulaUtils,
        TestAlertScripts,
        TestConfigurationFiles,
        TestScriptFiles
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果摘要
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # 返回成功状态
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)