import ConfirmDeleteModal from "./ConfirmDeleteModal";

interface Props {
  colorName: string;
  onCancel: () => void;
  onConfirm: () => void;
  confirming?: boolean;
}

export default function DeleteColorModal({ colorName, onCancel, onConfirm, confirming }: Props) {
  return (
    <ConfirmDeleteModal
      title="Delete color?"
      warning="Stock counts for this color will be removed permanently. This cannot be undone."
      onCancel={onCancel}
      onConfirm={onConfirm}
      confirming={confirming}
    >
      <p style={{ margin: 0 }}>
        Are you sure you want to delete the color <strong>{colorName}</strong>?
      </p>
    </ConfirmDeleteModal>
  );
}
