import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Data } from './data.entity';
import { FindOptionsWhere, Repository } from 'typeorm';
import { NewDataInput } from './dto/data.args';

@Injectable()
export class DataService {
	constructor(
		@InjectRepository(Data)
		private datasRepository: Repository<Data>,
	) {}

	findAll(): Promise<Data[]> {
		return this.datasRepository.find();
	}

	findOneBy(where: FindOptionsWhere<Data>): Promise<Data> {
		return this.datasRepository.findOneBy(where);
	}

	async remove(id: number): Promise<void> {
		await this.datasRepository.delete(id);
	}

	async create(newDataInput: NewDataInput): Promise<Data> {
		return await this.datasRepository.create(newDataInput);
	}
}
