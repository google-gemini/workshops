export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-4xl font-bold mb-6">About Little PAIPer</h1>
      <p className="text-lg text-gray-700 mb-4">
        Little PAIPer is an interactive learning platform designed to help
        users explore and understand concepts from various technical sources, the first one being {" "}
        <a
          href="https://www.amazon.com/Programming-Artificial-Intelligence-Python-Examples/dp/1484279029"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          "Programming Artificial Intelligence with Python Examples" (PAIP)
        </a>{" "}
        by Peter Norvig.
      </p>
      <p className="text-lg text-gray-700 mb-4">
        This platform focuses on providing a guided, socratic dialogue-based
        learning experience, allowing users to delve into complex AI topics
        through interactive examples, explanations, and a conversational AI
        tutor. It was created by Peter Norvig and Peter Danenberg.
      </p>
      <p className="text-lg text-gray-700 mb-4">
        The goal is to make advanced AI concepts accessible and engaging,
        fostering deeper understanding through active learning and
        personalized feedback.
      </p>
      <div className="mt-8 text-gray-600 text-sm">
        <p>
          For more information, please refer to the{" "}
          <a
            href="https://github.com/google-gemini/workshops/tree/main/learning" // TODO: Replace with actual repository link
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            project repository on GitHub
          </a>
          .
        </p>
      </div>
    </div>
  );
}
