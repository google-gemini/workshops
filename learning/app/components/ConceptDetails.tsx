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

type MasteryRecord = {
  conceptId: string;
  masteredAt: number;
};

type ConceptDetailsProps = {
  concept: Concept | null;
  onStartLearning?: (conceptId: string) => void;
  masteryRecord?: MasteryRecord | null;
  conceptStatus?: 'mastered' | 'recommended' | 'ready' | 'locked' | null;
};

export default function ConceptDetails({ concept, onStartLearning, masteryRecord, conceptStatus }: ConceptDetailsProps) {
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

  const statusConfig: Record<string, { label: string; color: string; icon: string }> = {
    mastered: { label: 'Mastered', color: 'bg-yellow-500', icon: '✓' },
    recommended: { label: 'Recommended Next', color: 'bg-green-500', icon: '⭐' },
    ready: { label: 'Ready to Learn', color: 'bg-blue-500', icon: '✅' },
    locked: { label: 'Locked', color: 'bg-gray-400', icon: '🔒' },
  };

  return (
    <Card className="h-full overflow-auto">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <CardTitle>{concept.name}</CardTitle>
              {conceptStatus && statusConfig[conceptStatus] && (
                <Badge className={`${statusConfig[conceptStatus].color} text-white`}>
                  {statusConfig[conceptStatus].icon} {statusConfig[conceptStatus].label}
                </Badge>
              )}
            </div>
            <CardDescription className="mt-2">{concept.description}</CardDescription>
            {masteryRecord && (
              <div className="mt-2 text-xs text-green-600 font-medium">
                ✓ Mastered {new Date(masteryRecord.masteredAt).toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            )}
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
