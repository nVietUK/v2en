import { Column, Entity, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Data {
	@PrimaryGeneratedColumn()
	id: number;

	@Column()
	origin: string;

	@Column()
	translated: string;

	@Column()
	translator: string;

	@Column({ nullable: false })
	hashValue: string;

	@Column({ default: false })
	verified: boolean;
}
