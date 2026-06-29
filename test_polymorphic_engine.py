#!/usr/bin/env python3
"""
Comprehensive test suite for the Polymorphic Engine
Tests algorithm correctness, variations, and functionality
"""

import unittest
import sys
import hashlib
from polymorphic_engine import (
    PolymorphicCodeGenerator,
    PolymorphicConfig,
    AlgorithmVariant,
    ControlFlowPattern,
)


class TestPolymorphicEngineBasics(unittest.TestCase):
    """Test basic functionality"""

    def setUp(self):
        self.config = PolymorphicConfig(seed=42)
        self.engine = PolymorphicCodeGenerator(self.config)
        self.test_data = b"Hello World"

    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.config.seed, 42)

    def test_random_name_generation(self):
        """Test random variable name generation"""
        name1 = self.engine.generate_random_name("test")
        name2 = self.engine.generate_random_name("test")
        self.assertNotEqual(name1, name2)
        self.assertTrue(name1.startswith("test_"))
        self.assertTrue(name2.startswith("test_"))

    def test_data_encoding_returns_tuple(self):
        """Test encoding returns correct tuple structure"""
        encoded, metadata, algo = self.engine.encode_data(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertIsInstance(metadata, dict)
        self.assertIsInstance(algo, str)
        self.assertIn("decoder", metadata)

    def test_encoded_data_different_from_original(self):
        """Test encoded data is different from original"""
        encoded, _, _ = self.engine.encode_data(self.test_data)
        self.assertNotEqual(encoded, self.test_data)

    def test_seed_parameter_accepted(self):
        """Test seed parameter is accepted"""
        config_with_seed = PolymorphicConfig(seed=123)
        config_without_seed = PolymorphicConfig(seed=None)

        self.assertEqual(config_with_seed.seed, 123)
        self.assertIsNone(config_without_seed.seed)

    def test_no_seed_produces_variations(self):
        """Test randomization without seed"""
        engines = [
            PolymorphicCodeGenerator(PolymorphicConfig(seed=None))
            for _ in range(5)
        ]

        algorithms = [engine.encode_data(self.test_data)[2] for engine in engines]

        # Check that we get some variation
        unique_algorithms = len(set(algorithms))
        self.assertGreater(unique_algorithms, 1)


class TestEncodingAlgorithms(unittest.TestCase):
    """Test individual encoding algorithms"""

    def setUp(self):
        self.engine = PolymorphicCodeGenerator()
        self.test_data = b"TEST"

    def test_linear_xor_encoding(self):
        """Test linear XOR encoding"""
        encoded, metadata = self.engine.gen_linear_xor(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))
        self.assertIn("key", metadata)
        self.assertIn("offset", metadata)
        self.assertNotEqual(encoded, self.test_data)

    def test_bitwise_rot_encoding(self):
        """Test bitwise rotation encoding"""
        encoded, metadata = self.engine.gen_bitwise_rot(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))
        self.assertIn("rotations", metadata)

    def test_math_offset_encoding(self):
        """Test mathematical offset encoding"""
        encoded, metadata = self.engine.gen_math_offset(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))
        self.assertIn("multiplier", metadata)
        self.assertIn("shift", metadata)

    def test_interleave_reverse_encoding(self):
        """Test interleave and reverse encoding"""
        encoded, metadata = self.engine.gen_interleave_reverse(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))

    def test_lookup_table_encoding(self):
        """Test lookup table encoding"""
        encoded, metadata = self.engine.gen_lookup_table(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))
        self.assertIn("table", metadata)
        self.assertEqual(len(metadata["table"]), 256)

    def test_chaotic_shuffle_encoding(self):
        """Test chaotic shuffling encoding"""
        encoded, metadata = self.engine.gen_chaotic_shuffle(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))
        self.assertIn("shuffle_indices", metadata)

    def test_wave_pattern_encoding(self):
        """Test wave pattern encoding"""
        encoded, metadata = self.engine.gen_wave_pattern(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))

    def test_prime_modulo_encoding(self):
        """Test prime modulo encoding"""
        encoded, metadata = self.engine.gen_prime_modulo(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))
        self.assertIn("prime", metadata)
        self.assertIn("offset", metadata)

    def test_fibonacci_sequence_encoding(self):
        """Test Fibonacci sequence encoding"""
        encoded, metadata = self.engine.gen_fibonacci_sequence(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))

    def test_recursive_split_encoding(self):
        """Test recursive split encoding"""
        encoded, metadata = self.engine.gen_recursive_split(self.test_data)
        self.assertIsInstance(encoded, bytes)
        self.assertEqual(len(encoded), len(self.test_data))


class TestDecoderGeneration(unittest.TestCase):
    """Test decoder code generation"""

    def setUp(self):
        self.engine = PolymorphicCodeGenerator()
        self.test_data = b"TESTDATA"

    def test_decoder_generation_returns_string(self):
        """Test decoder generation returns Python code"""
        encoded, metadata, _ = self.engine.encode_data(self.test_data)
        decoder = self.engine.generate_polymorphic_decoder(encoded, metadata)

        self.assertIsInstance(decoder, str)
        self.assertGreater(len(decoder), 0)
        # Check for Python syntax elements
        self.assertTrue(
            any(keyword in decoder for keyword in ["def", "for", "=", "bytes"])
        )

    def test_decoder_has_variable_assignment(self):
        """Test generated decoder assigns to variable"""
        encoded, metadata, _ = self.engine.encode_data(self.test_data)
        decoder = self.engine.generate_polymorphic_decoder(encoded, metadata)

        self.assertIn("=", decoder)

    def test_decoder_length_varies(self):
        """Test decoder length varies between algorithms"""
        lengths = []

        for _ in range(10):
            encoded, metadata, _ = self.engine.encode_data(self.test_data)
            decoder = self.engine.generate_polymorphic_decoder(encoded, metadata)
            lengths.append(len(decoder))

        # Should have some variation in lengths
        unique_lengths = len(set(lengths))
        self.assertGreater(unique_lengths, 1)


class TestPolymorphicGeneration(unittest.TestCase):
    """Test complete polymorphic generation"""

    def setUp(self):
        self.command = "echo test"

    def test_complete_script_generation(self):
        """Test complete polymorphic script generation"""
        engine = PolymorphicCodeGenerator()
        script = engine.generate_complete_polymorphic_script(self.command)

        self.assertIsInstance(script, str)
        self.assertGreater(len(script), 0)
        self.assertIn("#!/usr/bin/env python3", script)
        self.assertIn("subprocess", script)

    def test_multi_stage_generation(self):
        """Test multi-stage polymorphic generation"""
        engine = PolymorphicCodeGenerator()
        script = engine.generate_multi_stage_polymorphic(self.command, stages=3)

        self.assertIsInstance(script, str)
        # Should have markers for stages
        self.assertIn("Stage 1", script)
        self.assertIn("Stage 2", script)
        self.assertIn("Stage 3", script)

    def test_scripts_are_different(self):
        """Test multiple generations produce different scripts"""
        scripts = []

        for _ in range(3):
            engine = PolymorphicCodeGenerator()
            script = engine.generate_complete_polymorphic_script(self.command)
            scripts.append(script)

        # Should have different content
        unique_scripts = len(set(scripts))
        self.assertEqual(unique_scripts, 3)


class TestVariableGeneration(unittest.TestCase):
    """Test variable name generation and tracking"""

    def test_variable_counter_increments(self):
        """Test variable counter increments"""
        engine = PolymorphicCodeGenerator()

        initial_count = engine.var_counter
        engine.generate_random_name("test")
        self.assertEqual(engine.var_counter, initial_count + 1)

        engine.generate_random_name("test")
        self.assertEqual(engine.var_counter, initial_count + 2)

    def test_unique_variable_names(self):
        """Test generated variable names are unique"""
        engine = PolymorphicCodeGenerator()
        names = set()

        for _ in range(100):
            name = engine.generate_random_name("var")
            self.assertNotIn(name, names)
            names.add(name)

    def test_generation_info(self):
        """Test generation info is accurate"""
        config = PolymorphicConfig(
            algorithm_variants=2,
            control_flow_patterns=3,
            complexity_level=4,
        )
        engine = PolymorphicCodeGenerator(config)

        info = engine.get_generation_info()

        self.assertEqual(info["algorithm_variants"], 2)
        self.assertEqual(info["control_flow_patterns"], 3)
        self.assertEqual(info["complexity_level"], 4)
        self.assertIn("variables_generated", info)


class TestDataLength(unittest.TestCase):
    """Test encoding with different data lengths"""

    def setUp(self):
        self.engine = PolymorphicCodeGenerator()

    def test_single_byte_encoding(self):
        """Test encoding single byte"""
        encoded, metadata, _ = self.engine.encode_data(b"A")
        self.assertEqual(len(encoded), 1)

    def test_empty_data_handling(self):
        """Test encoding empty data"""
        encoded, metadata, _ = self.engine.encode_data(b"")
        self.assertEqual(len(encoded), 0)

    def test_large_data_encoding(self):
        """Test encoding large data"""
        large_data = b"X" * 1000
        encoded, metadata, _ = self.engine.encode_data(large_data)
        self.assertEqual(len(encoded), 1000)

    def test_binary_data_encoding(self):
        """Test encoding binary data with all byte values"""
        binary_data = bytes(range(256))
        encoded, metadata, _ = self.engine.encode_data(binary_data)
        self.assertEqual(len(encoded), 256)


class TestControlFlowWrapping(unittest.TestCase):
    """Test control flow wrapping variations"""

    def setUp(self):
        self.engine = PolymorphicCodeGenerator()
        self.test_code = "x = 1"

    def test_sequential_wrapping(self):
        """Test sequential control flow"""
        wrapped = self.engine._wrap_sequential(self.test_code, "result")
        self.assertEqual(wrapped, self.test_code)

    def test_conditional_wrapping(self):
        """Test conditional control flow"""
        wrapped = self.engine._wrap_conditional(self.test_code, "result")
        self.assertIn("if", wrapped)
        self.assertIn("else", wrapped)

    def test_loop_wrapping(self):
        """Test loop control flow"""
        wrapped = self.engine._wrap_loop(self.test_code, "result")
        self.assertIn("for", wrapped)
        self.assertIn("range(1)", wrapped)

    def test_state_machine_wrapping(self):
        """Test state machine control flow"""
        wrapped = self.engine._wrap_state_machine(self.test_code, "result")
        self.assertIn("while", wrapped)


class TestConfiguration(unittest.TestCase):
    """Test configuration options"""

    def test_default_configuration(self):
        """Test default configuration values"""
        config = PolymorphicConfig()

        self.assertIsNone(config.seed)
        self.assertEqual(config.algorithm_variants, 3)
        self.assertEqual(config.control_flow_patterns, 2)
        self.assertEqual(config.target_language, "python")
        self.assertEqual(config.complexity_level, 3)

    def test_custom_configuration(self):
        """Test custom configuration"""
        config = PolymorphicConfig(
            seed=12345,
            algorithm_variants=5,
            complexity_level=5,
        )

        self.assertEqual(config.seed, 12345)
        self.assertEqual(config.algorithm_variants, 5)
        self.assertEqual(config.complexity_level, 5)

    def test_engine_with_config(self):
        """Test engine respects configuration"""
        config = PolymorphicConfig(complexity_level=1)
        engine = PolymorphicCodeGenerator(config)

        self.assertEqual(engine.config.complexity_level, 1)


def run_tests_with_summary():
    """Run all tests and provide summary"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPolymorphicEngineBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestEncodingAlgorithms))
    suite.addTests(loader.loadTestsFromTestCase(TestDecoderGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestPolymorphicGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestVariableGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLength))
    suite.addTests(loader.loadTestsFromTestCase(TestControlFlowWrapping))
    suite.addTests(loader.loadTestsFromTestCase(TestConfiguration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests_with_summary()
    sys.exit(0 if success else 1)
