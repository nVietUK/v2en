import { Field, ObjectType } from '@nestjs/graphql';
import { Md5 } from 'ts-md5';
import { Column, Entity, PrimaryGeneratedColumn } from 'typeorm';

@Entity({ name: 'Data' })
@ObjectType()
export class Data {
	constructor(origin = '', translated = '', translator = '', verified = false) {
		this.origin = origin;
		this.translated = translated;
		this.translator = translator;
		this.verified = verified;
	}

	@PrimaryGeneratedColumn('uuid')
	id: number | undefined;

	@Column('int')
	@Field(() => String, { description: 'the origin of sentence' })
	origin: string;

	@Column()
	@Field(() => String, { description: 'the translated of sentence' })
	translated: string;

	@Column()
	@Field(() => String, { description: "the sentence's translator" })
	translator: string;

	@Column({ nullable: false })
	get hashValue(): string {
		return Md5.hashStr(`${this.origin} ${this.translated} ${this.translator}`);
	}

	@Column({ default: false })
	@Field(() => Boolean, { description: 'confirm that data is verified by authorizer' })
	verified: boolean;
}
