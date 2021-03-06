import unittest

import ray
from ray.rllib.agents.a3c import A2CTrainer


class TestPipeline(unittest.TestCase):
    """General tests for the pipeline API."""

    @classmethod
    def setUpClass(cls):
        ray.init()

    @classmethod
    def tearDownClass(cls):
        ray.shutdown()

    def test_pipeline_stats(ray_start_regular):
        trainer = A2CTrainer(
            env="CartPole-v0",
            config={
                "min_iter_time_s": 0,
                "use_pipeline_impl": True
            })
        result = trainer.train()
        assert isinstance(result, dict)
        assert "info" in result
        assert "learner" in result["info"]
        assert "num_steps_sampled" in result["info"]
        assert "num_steps_trained" in result["info"]
        assert "timers" in result
        assert "learn_time_ms" in result["timers"]
        assert "learn_throughput" in result["timers"]
        assert "sample_time_ms" in result["timers"]
        assert "sample_throughput" in result["timers"]
        assert "update_time_ms" in result["timers"]

    def test_pipeline_save_restore(ray_start_regular):
        trainer = A2CTrainer(
            env="CartPole-v0",
            config={
                "min_iter_time_s": 0,
                "use_pipeline_impl": True
            })
        res1 = trainer.train()
        checkpoint = trainer.save()
        res2 = trainer.train()
        assert res2["timesteps_total"] > res1["timesteps_total"], (res1, res2)
        trainer.restore(checkpoint)

        # Should restore the timesteps counter to the same as res2.
        res3 = trainer.train()
        assert res3["timesteps_total"] == res2["timesteps_total"], (res2, res3)


if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main(["-v", __file__]))
