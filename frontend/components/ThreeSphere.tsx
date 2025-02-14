"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Sphere } from "@react-three/drei";

export const ThreeSphere = () => {
  return (
    <Canvas>
      <OrbitControls enableZoom={false} />
      <ambientLight intensity={0.5} />
      <directionalLight position={[2, 2, 5]} intensity={1} />
      <Sphere args={[1, 100, 200]} scale={2.4}>
        <meshStandardMaterial
          color="#00ff83"
          wireframe
          transparent
          opacity={0.15}
        />
      </Sphere>
    </Canvas>
  );
};
