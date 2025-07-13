fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto_dir = "../proto"; // Relative path to the top-level proto directory

    println!("cargo:rerun-if-changed={}", proto_dir);

    tonic_build::configure()
        .build_server(false) // We are only building the client
        .build_client(true)
        .out_dir("src/proto") // Output generated code to src/proto
        .compile(
            &[
                format!("{}/ast_schemas.proto", proto_dir),
                format!("{}/ast_service.proto", proto_dir),
            ],
            &[proto_dir], // Include path for Protobuf imports
        )?;

    Ok(())
}