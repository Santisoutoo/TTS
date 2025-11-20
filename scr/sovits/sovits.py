import os
import sys
import torch
import librosa
import soundfile as sf
import numpy as np
from typing import Optional
import warnings

warnings.filterwarnings('ignore')


class GPTSoVITS:
    """
    GPT-SoVITS implementation for zero-shot voice cloning.

    GPT-SoVITS is a TTS model that combines:
    - GPT for generating semantic features of speech
    - SoVITS (based on VITS) for high-quality audio synthesis

    References:
    - Official repository: https://github.com/RVC-Boss/GPT-SoVITS
    """

    def __init__(
        self,
        gpt_model_path: Optional[str] = None,
        sovits_model_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Initialize GPT-SoVITS with specified models.

        Args:
            gpt_model_path: Path to pre-trained GPT model
            sovits_model_path: Path to pre-trained SoVITS model
            device: Device to use ('cuda' or 'cpu')
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"Initializing GPT-SoVITS")
        print(f"Using device: {self.device}")

        # Default paths for pre-trained models
        self.gpt_model_path = gpt_model_path or "models/gpt_sovits/gpt.ckpt"
        self.sovits_model_path = sovits_model_path or "models/gpt_sovits/sovits.pth"

        # Try to load native GPT-SoVITS implementation
        self.use_native_api = False
        try:
            self._load_native_implementation()
            self.use_native_api = True
            print("Using native GPT-SoVITS implementation")
        except ImportError as e:
            print(f"Native implementation not available: {e}")
            print("Using alternative implementation")
            self._setup_alternative_implementation()

    def _load_native_implementation(self):
        """
        Try to load native GPT-SoVITS implementation.
        """
        try:
            # Try to import GPT-SoVITS modules
            from GPT_SoVITS.inference_webui import get_tts_wav
            self.inference_fn = get_tts_wav
        except ImportError:
            # If not installed as package, try to import from directory
            gpt_sovits_path = os.path.join(os.path.dirname(__file__), "GPT-SoVITS")
            if os.path.exists(gpt_sovits_path):
                sys.path.insert(0, gpt_sovits_path)
                from GPT_SoVITS.inference_webui import get_tts_wav
                self.inference_fn = get_tts_wav
            else:
                raise ImportError("GPT-SoVITS is not installed")

    def _setup_alternative_implementation(self):
        """
        Set up alternative implementation using REST API or simplified approach.
        """
        # Configuration parameters
        self.sample_rate = 32000
        self.hop_length = 512

        print("Using simplified voice cloning implementation")
        print("NOTE: For best results, install GPT-SoVITS from:")
        print("  https://github.com/RVC-Boss/GPT-SoVITS")

    def _preprocess_audio(
        self,
        audio_path: str,
        target_sr: int = 32000
    ) -> np.ndarray:
        """
        Preprocess reference audio.

        Args:
            audio_path: Path to audio file
            target_sr: Target sample rate

        Returns:
            Numpy array with processed audio
        """
        # Load audio
        audio, sr = librosa.load(audio_path, sr=target_sr)

        # Normalize
        audio = audio / np.max(np.abs(audio))

        return audio

    def _extract_reference_features(
        self,
        reference_audio: np.ndarray
    ) -> dict:
        """
        Extract features from reference audio for voice cloning.

        Args:
            reference_audio: Reference audio array

        Returns:
            Dictionary with extracted features
        """
        # In a complete implementation, this would extract:
        # - Speaker embeddings with GPT model
        # - Prosodic features
        # - Spectral features

        features = {
            'audio': reference_audio,
            'length': len(reference_audio),
            'mean_energy': np.mean(np.abs(reference_audio)),
            'std_energy': np.std(np.abs(reference_audio))
        }

        return features

    def synthesize(
        self,
        text: str,
        output_path: str,
        reference_audio_path: str,
        language: str = "es",
        top_k: int = 20,
        top_p: float = 0.8,
        temperature: float = 0.8,
        text_split_method: str = "cut5",
        speed: float = 1.0
    ) -> str:
        """
        Synthesize audio using GPT-SoVITS with voice cloning.

        Args:
            text: Text to synthesize
            output_path: Path to save generated audio
            reference_audio_path: Path to reference audio for voice cloning
            language: Text language ('es', 'en', 'zh', 'ja', etc.)
            top_k: Top-k parameter for GPT model sampling
            top_p: Top-p (nucleus sampling) parameter for GPT model
            temperature: Temperature for sampling (higher = more variation)
            text_split_method: Method to split long text
            speed: Playback speed (1.0 = normal)

        Returns:
            Path to generated audio file
        """
        print(f"\nSynthesizing with GPT-SoVITS:")
        print(f"  Text: '{text[:60]}...'")
        print(f"  Reference audio: {reference_audio_path}")
        print(f"  Language: {language}")

        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            if self.use_native_api:
                # Use native GPT-SoVITS API
                audio_output = self._synthesize_native(
                    text=text,
                    reference_audio_path=reference_audio_path,
                    language=language,
                    top_k=top_k,
                    top_p=top_p,
                    temperature=temperature,
                    text_split_method=text_split_method,
                    speed=speed
                )
            else:
                # Use alternative implementation
                audio_output = self._synthesize_alternative(
                    text=text,
                    reference_audio_path=reference_audio_path,
                    language=language
                )

            # Save audio
            sf.write(output_path, audio_output, self.sample_rate)
            print(f"Audio generated successfully: {output_path}")

            return output_path

        except Exception as e:
            print(f"Error during synthesis: {e}")
            raise

    def _synthesize_native(
        self,
        text: str,
        reference_audio_path: str,
        language: str,
        top_k: int,
        top_p: float,
        temperature: float,
        text_split_method: str,
        speed: float
    ) -> np.ndarray:
        """
        Synthesize using native GPT-SoVITS API.
        """
        # Call native inference function
        result = self.inference_fn(
            text=text,
            text_lang=language,
            ref_audio_path=reference_audio_path,
            prompt_text="",  # Reference audio text (optional)
            prompt_lang=language,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            text_split_method=text_split_method,
            batch_size=1,
            speed_factor=speed,
            split_bucket=True,
            return_fragment=False
        )

        # API returns generated audio
        return result

    def _synthesize_alternative(
        self,
        text: str,
        reference_audio_path: str,
        language: str
    ) -> np.ndarray:
        """
        Simplified alternative implementation.

        NOTE: This is a fallback implementation that does NOT provide
        the same quality as real GPT-SoVITS. Full installation is recommended.
        """
        print("\n WARNING: Using simplified implementation")
        print("   For production results, install full GPT-SoVITS")

        # Load reference audio
        ref_audio = self._preprocess_audio(reference_audio_path, self.sample_rate)

        # Extract features
        ref_features = self._extract_reference_features(ref_audio)

        # Generate basic synthetic audio
        # In production, this would come from the model
        duration = len(text) * 0.1  # ~100ms per character
        num_samples = int(duration * self.sample_rate)

        # Generate base signal
        # (In production, this would come from the model)
        t = np.linspace(0, duration, num_samples)

        # Use reference audio features to modulate
        base_freq = 200  # Hz (typical fundamental frequency)
        audio = np.sin(2 * np.pi * base_freq * t)

        # Apply envelope based on reference audio
        envelope = np.abs(ref_audio[:min(len(ref_audio), num_samples)])
        if len(envelope) < num_samples:
            envelope = np.pad(envelope, (0, num_samples - len(envelope)), mode='edge')
        else:
            envelope = envelope[:num_samples]

        audio = audio * envelope * 0.3

        print("\n WARNING: Audio generated with simplified synthesis")
        print("   NOT comparable to real GPT-SoVITS")

        return audio.astype(np.float32)

    def batch_synthesize(
        self,
        text_list: list,
        output_dir: str,
        reference_audio_path: str,
        language: str = "es",
        **kwargs
    ) -> list:
        """
        Synthesize multiple texts in batch mode.

        Args:
            text_list: List of texts to synthesize
            output_dir: Directory to save audio files
            reference_audio_path: Reference audio for voice cloning
            language: Language of texts
            **kwargs: Additional parameters for synthesize()

        Returns:
            List of paths to generated files
        """
        os.makedirs(output_dir, exist_ok=True)
        output_paths = []

        print(f"\nSynthesizing {len(text_list)} texts in batch mode...")

        for i, text in enumerate(text_list):
            output_path = os.path.join(output_dir, f"output_{i:03d}.wav")

            try:
                self.synthesize(
                    text=text,
                    output_path=output_path,
                    reference_audio_path=reference_audio_path,
                    language=language,
                    **kwargs
                )
                output_paths.append(output_path)
            except Exception as e:
                print(f"Error synthesizing text {i}: {e}")
                continue

        print(f"Batch completed: {len(output_paths)}/{len(text_list)} successful")
        return output_paths

    def get_model_info(self) -> dict:
        """
        Return information about loaded models.
        """
        return {
            'gpt_model_path': self.gpt_model_path,
            'sovits_model_path': self.sovits_model_path,
            'device': self.device,
            'using_native_api': self.use_native_api,
            'sample_rate': self.sample_rate
        }
