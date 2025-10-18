plugins {
    kotlin("jvm") version "1.9.0"
    `maven-publish`
}

group = "com.monta"
version = "0.1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.xerial:sqlite-jdbc:3.43.0.0")
    testImplementation(kotlin("test"))
    testImplementation("com.google.code.gson:gson:2.10.1")
}

kotlin {
    jvmToolchain(11)
}

tasks.test {
    useJUnitPlatform()
}

publishing {
    publications {
        create<MavenPublication>("maven") {
            from(components["java"])
        }
    }
}
