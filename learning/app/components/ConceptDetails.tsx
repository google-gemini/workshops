import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

type Concept = {
  id: string;
  name: string;
  description: string;
  difficulty: string;
  prerequisites: string[];
  learning_objectives?: string[];
  mastery_indicators?: any[];
  examples?: any[];
  misconceptions?: any[];
  key_insights?: any[];
};

type ConceptDetailsProps = {
  concept: Concept | null;
  onStartLearning?: (conceptId: string) => void;
};

export default function ConceptDetails({ concept, onStartLearning }: ConceptDetailsProps) {
  if (!concept) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Select a Concept</CardTitle>
          <CardDescription>Click on any node in the graph to see details</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const difficultyColors: Record<string, string> = {
    basic: 'bg-green-500',
    intermediate: 'bg-blue-500',
    advanced: 'bg-red-500',
  };

  return (
    <Card className="h-full overflow-auto">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{concept.name}</CardTitle>
            <CardDescription className="mt-2">{concept.description}</CardDescription>
          </div>
          <Badge className={difficultyColors[concept.difficulty]}>{concept.difficulty}</Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Prerequisites */}
        {concept.prerequisites.length > 0 && (
          <div>
            <h3 className="font-semibold text-sm mb-2">Prerequisites:</h3>
            <div className="flex flex-wrap gap-2">
              {concept.prerequisites.map((prereq) => (
                <Badge key={prereq} variant="outline">
                  {prereq}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Learning Objectives */}
        {concept.learning_objectives && concept.learning_objectives.length > 0 && (
          <div>
            <h3 className="font-semibold text-sm mb-2">Learning Objectives:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm">
              {concept.learning_objectives.map((obj, i) => (
                <li key={i}>{obj}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Key Insights */}
        {concept.key_insights && concept.key_insights.length > 0 && (
          <div>
            <h3 className="font-semibold text-sm mb-2">Key Insights:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
              {concept.key_insights.map((insight, i) => (
                <li key={i}>{insight}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Start Learning Button */}
        {onStartLearning && (
          <Button onClick={() => onStartLearning(concept.id)} className="w-full mt-4">
            Start Learning
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
