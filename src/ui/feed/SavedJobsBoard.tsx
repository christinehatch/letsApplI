import React from "react";
import {
  DndContext,
  DragOverlay,
  type DragEndEvent,
  type DragStartEvent,
  PointerSensor,
  useDroppable,
  useSensor,
  useSensors,
  closestCenter,
} from "@dnd-kit/core";
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { JobCard } from "./JobCard";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
  url?: string;
  posted_at?: string | null;
  provider?: string;
  state?: string | null;
  ai_relevance_score?: number | null;
  raw_provider_payload_json?: string | null;
};

type SavedJobsBoardProps = {
  jobsByState: Record<string, Job[]>;
  selectedJob: Job | null;
  onSelectJob: (job: Job) => void;
  onSaveJob: (jobId: string, currentState?: string | null) => void;
  onUpdateJobState: (jobId: string, newState: string) => void;
};

const PIPELINE_STATES = ["saved", "applied", "interview", "offer"] as const;

function SortableJobCard({
  job,
  selected,
  onSelectJob,
  onSaveJob,
  onUpdateJobState,
}: {
  job: Job;
  selected: boolean;
  onSelectJob: (job: Job) => void;
  onSaveJob: (jobId: string, currentState?: string | null) => void;
  onUpdateJobState: (jobId: string, newState: string) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: job.id,
  });

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.7 : 1,
    touchAction: "none",
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <JobCard
        job={job}
        selected={selected}
        onClick={() => onSelectJob(job)}
        onSave={() => onSaveJob(job.id, job.state)}
        onStatusChange={(newStatus) => onUpdateJobState(job.id, newStatus)}
      />
    </div>
  );
}

function DropColumn({ state, children }: { state: string; children: React.ReactNode }) {
  const { setNodeRef, isOver } = useDroppable({ id: state });

  return (
    <div
      ref={setNodeRef}
      style={{
        background: isOver ? "#f0f7ff" : "#fafafa",
        border: "1px solid #eee",
        borderRadius: "8px",
        padding: "10px",
        minHeight: "140px",
      }}
    >
      {children}
    </div>
  );
}

export function SavedJobsBoard({
  jobsByState,
  selectedJob,
  onSelectJob,
  onSaveJob,
  onUpdateJobState,
}: SavedJobsBoardProps) {
  const sensors = useSensors(useSensor(PointerSensor));
  const [activeJob, setActiveJob] = React.useState<Job | null>(null);

  const allJobs = PIPELINE_STATES.flatMap((state) => jobsByState[state] ?? []);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    const jobId = String(active.id);
    const dragged = allJobs.find((job) => job.id === jobId);
    if (!dragged) return;

    const overId = String(over.id);
    let newState = overId;

    if (!PIPELINE_STATES.includes(overId as (typeof PIPELINE_STATES)[number])) {
      const overJob = allJobs.find((job) => job.id === overId);
      if (!overJob || !overJob.state) return;
      newState = overJob.state;
    }

    if (dragged.state === newState) return;
    onUpdateJobState(jobId, newState);
  };

  const handleDragStart = (event: DragStartEvent) => {
    const jobId = String(event.active.id);
    const dragged = allJobs.find((job) => job.id === jobId) ?? null;
    setActiveJob(dragged);
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={(event) => {
        handleDragEnd(event);
        setActiveJob(null);
      }}
      onDragCancel={() => setActiveJob(null)}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "12px",
        }}
      >
        {PIPELINE_STATES.map((state) => {
          const columnJobs = jobsByState[state] ?? [];
          return (
            <div key={state}>
              <h4 style={{ marginBottom: "10px", textTransform: "capitalize" }}>{state}</h4>
              <DropColumn state={state}>
                <SortableContext items={columnJobs.map((job) => job.id)} strategy={verticalListSortingStrategy}>
                  {columnJobs.map((job) => (
                    <SortableJobCard
                      key={job.id}
                      job={job}
                      selected={selectedJob?.id === job.id}
                      onSelectJob={onSelectJob}
                      onSaveJob={onSaveJob}
                      onUpdateJobState={onUpdateJobState}
                    />
                  ))}
                </SortableContext>
              </DropColumn>
            </div>
          );
        })}
      </div>
      <DragOverlay>
        {activeJob ? (
          <div style={{ width: "280px" }}>
            <JobCard
              job={activeJob}
              selected={false}
              onClick={() => {}}
              onSave={() => {}}
              isDragging
            />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
